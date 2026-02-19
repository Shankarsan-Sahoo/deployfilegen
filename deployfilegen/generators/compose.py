from pathlib import Path
from typing import List, Optional


def generate_docker_compose(mode: str, config: dict, with_db: bool = False,
                            env_files: Optional[List[Path]] = None,
                            project_root: Optional[Path] = None,
                            frontend_port: int = 3000,
                            deploy: str = "ssh") -> str:
    """
    Generates docker-compose.yml for production or dev.
    
    Deploy strategy only affects prod mode:
      - 'ssh': services use build: (images built on server)
      - 'registry': services use image: (images pulled from registry)
    
    Dev mode always uses build: with volume mounts.
    """
    env_file_refs = _compute_env_refs(env_files, project_root)
    
    if mode == "dev":
        return _generate_dev_compose(with_db, env_file_refs, frontend_port)
    else:
        return _generate_prod_compose(with_db, env_file_refs, deploy)


def _compute_env_refs(env_files: Optional[List[Path]], project_root: Optional[Path]) -> List[str]:
    """Compute relative .env paths from project root."""
    env_file_refs = []
    if env_files and project_root:
        for ef in env_files:
            try:
                rel = ef.relative_to(project_root)
                env_file_refs.append(f"./{rel.as_posix()}")
            except ValueError:
                env_file_refs.append(str(ef))
    return env_file_refs or ["./.env"]


def _build_env_file_block(env_file_refs: List[str]) -> str:
    """Builds the env_file YAML block."""
    lines = "\n".join(f"      - {ref}" for ref in env_file_refs)
    return f"    env_file:\n{lines}"


# ─── PRODUCTION ───────────────────────────────────────────────

def _generate_prod_compose(with_db: bool, env_file_refs: List[str], deploy: str) -> str:
    env_block = _build_env_file_block(env_file_refs)
    
    # Deploy strategy determines how services reference images
    if deploy == "registry":
        backend_source = "    image: ${BACKEND_IMAGE_NAME}:${IMAGE_TAG:-latest}"
        frontend_source = "    image: ${FRONTEND_IMAGE_NAME}:${IMAGE_TAG:-latest}"
    else:  # ssh
        backend_source = "    build:\n      context: ./backend"
        frontend_source = "    build:\n      context: ./frontend"
    
    db_service = ""
    db_depends = ""
    if with_db:
        db_service = f"""
  db:
    image: postgres:15-alpine
    restart: always
{env_block}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network
"""
        db_depends = """
    depends_on:
      db:
        condition: service_healthy"""

    return f"""services:
  backend:
{backend_source}
{env_block}
    restart: always{db_depends}
    ports:
      - "8000:8000"
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    networks:
      - app-network
{db_service}
  frontend:
{frontend_source}
    restart: always
    ports:
      - "80:8080"
    depends_on:
      - backend
    networks:
      - app-network

volumes:
  static_volume:
  media_volume:{"\\n  postgres_data:" if with_db else ""}

networks:
  app-network:
    driver: bridge
"""


# ─── DEVELOPMENT ──────────────────────────────────────────────

def _generate_dev_compose(with_db: bool, env_file_refs: List[str], frontend_port: int = 3000) -> str:
    env_block = _build_env_file_block(env_file_refs)
    
    db_service = ""
    db_depends = ""
    if with_db:
        db_service = f"""
  db:
    image: postgres:15-alpine
{env_block}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
"""
        db_depends = """
    depends_on:
      - db"""

    return f"""services:
  backend:
    build:
      context: ./backend
{env_block}{db_depends}
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    networks:
      - app-network
{db_service}
  frontend:
    build:
      context: ./frontend
    ports:
      - "{frontend_port}:{frontend_port}"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    stdin_open: true
    tty: true
    networks:
      - app-network
{"\\nvolumes:\\n  postgres_data:" if with_db else ""}
networks:
  app-network:
    driver: bridge
"""
