import typer
from pathlib import Path
from typing import Optional

from deployfilegen.utils.logger import logger
from deployfilegen.utils.writer import FileWriter
from deployfilegen.config.env_loader import load_environment, validate_environment
from deployfilegen.analyzer.detector import detect_django_backend, detect_react_frontend
from deployfilegen.generators.backend import generate_backend_dockerfile
from deployfilegen.generators.frontend import generate_frontend_dockerfile
from deployfilegen.generators.compose import generate_docker_compose
from deployfilegen.generators.github import generate_github_workflow
from deployfilegen.exceptions import DeployFileGenError, EnvConfigError
from deployfilegen import __version__

app = typer.Typer(no_args_is_help=True)

def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()

@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Show the version and exit."
    ),
):
    """
    A production-grade CLI tool to generate deployment configuration files.
    """
    pass

@app.command(name="init")
def init(
    mode: str = typer.Option("prod", help="Generation mode: 'prod' or 'dev'"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
    docker_only: bool = typer.Option(False, "--docker-only", help="Generate only Dockerfiles"),
    compose_only: bool = typer.Option(False, "--compose-only", help="Generate only Docker Compose"),
    github_only: bool = typer.Option(False, "--github-only", help="Generate only GitHub Actions"),
    backend_only: bool = typer.Option(False, "--backend-only", help="Generate only for Backend"),
    frontend_only: bool = typer.Option(False, "--frontend-only", help="Generate only for Frontend"),
    with_db: bool = typer.Option(False, "--with-db", help="Include a Postgres database service in Docker Compose"),
):
    """
    Initialize deployment configuration for the current project.
    """
    try:
        project_root = Path.cwd()
        # 1. Config & Validation
        load_environment(project_root)
        config = validate_environment()

        # 2. Detection
        try:
            backend_path = detect_django_backend(project_root)
            backend_detected = True
        except DeployFileGenError:
            backend_path = None
            backend_detected = False

        try:
            frontend_path = detect_react_frontend(project_root)
            frontend_detected = True
        except DeployFileGenError:
            frontend_path = None
            frontend_detected = False

        # 3. Initialization
        writer = FileWriter(force=force)

        # Targeted Logic
        any_type_flag = docker_only or compose_only or github_only
        do_docker = docker_only or not any_type_flag
        do_compose = compose_only or not any_type_flag
        do_github = github_only or not any_type_flag

        any_comp_flag = backend_only or frontend_only
        do_backend = backend_only or not any_comp_flag
        do_frontend = frontend_only or not any_comp_flag

        # 4. Generate Backend Dockerfile
        if do_docker and do_backend and backend_detected:
            typer.echo("Generating Backend Dockerfile...")
            backend_docker = generate_backend_dockerfile(mode, backend_path)
            if writer.write(backend_path / "Dockerfile", backend_docker):
                typer.echo("Generated backend/Dockerfile")
            writer.write(backend_path / ".dockerignore", "venv/\n__pycache__/\n*.pyc\n.git/\n.env\nstatic/\ntests/\n")

        # 5. Generate Frontend Dockerfile
        if do_docker and do_frontend and frontend_detected:
            typer.echo("Generating Frontend Dockerfile...")
            frontend_docker = generate_frontend_dockerfile(mode)
            if writer.write(frontend_path / "Dockerfile", frontend_docker):
                typer.echo("Generated frontend/Dockerfile")
            writer.write(frontend_path / ".dockerignore", "node_modules/\nbuild/\ncoverage/\n.git/\n.env\n")

        # 6. Generate docker-compose.yml
        if do_compose:
            typer.echo("Generating Docker Compose...")
            compose_content = generate_docker_compose(mode, config, with_db=with_db)
            compose_filename = "docker-compose.prod.yml" if mode == "prod" else "docker-compose.dev.yml"
            if writer.write(project_root / compose_filename, compose_content):
                typer.echo(f"Generated {compose_filename}")

        # 7. Generate GitHub Actions
        if do_github:
            typer.echo("Generating GitHub Actions workflow...")
            github_workflow = generate_github_workflow(config)
            github_dir = project_root / ".github" / "workflows"
            if writer.write(github_dir / "deploy.yml", github_workflow):
                typer.echo("Generated .github/workflows/deploy.yml")

        typer.echo("Deployment configuration generated successfully!")
        
        # Runtime Success Checklist
        typer.echo("\n--- 🏁 Deployment Success Checklist ---")
        typer.echo("1. Connection: Ensure your server can reach the internet and Docker Hub.")
        typer.echo("2. Database: Verify DATABASE_URL is accessible from the container.")
        typer.echo("3. Environment: Confirm your server's .env matches the generated template.")
        typer.echo("4. Images: Ensure build images are pushed to Docker Hub before deploying.")
        typer.echo("--------------------------------------")

    except EnvConfigError as e:
        typer.echo(f"Error: {e}")
        typer.echo("Tip: Run 'deployfilegen template' to generate a boilerplate .env file.")
        raise typer.Exit(code=1)
    except DeployFileGenError as e:
        logger.info("Error: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.exception(f"Unexpected Error: {e}")
        raise typer.Exit(code=1)

@app.command(name="template")
def generate_template(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .env file")
):
    """
    Generate a boilerplate .env file with required placeholders.
    """
    try:
        project_root = Path.cwd()
        env_path = project_root / ".env"
        
        template_content = """# deployfilegen Environment Template
# Fill in these values for production deployment

# Docker Hub Credentials
DOCKER_USERNAME=your_docker_username

# Image Names (e.g. username/repo)
BACKEND_IMAGE_NAME=your_docker_username/backend_image
FRONTEND_IMAGE_NAME=your_docker_username/frontend_image

# Deployment Server
DEPLOY_HOST=your_server_ip
DEPLOY_USER=your_ssh_user
"""
        writer = FileWriter(force=force)
        writer.write(env_path, template_content)
        typer.echo("Generated boilerplate .env file. Please fill in the values.")
        
    except DeployFileGenError as e:
        logger.info(f"Error: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.exception(f"Unexpected Error: {e}")
        raise typer.Exit(code=1)

def main():
    app()

if __name__ == "__main__":
    main()
