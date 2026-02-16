from typer.testing import CliRunner
from deployfilegen.cli import app
from pathlib import Path

runner = CliRunner()

def test_template_command(tmp_path):
    # Change CWD to tmp_path
    import os
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        result = runner.invoke(app, ["template"])
        assert result.exit_code == 0
        assert "Generated boilerplate .env file" in result.stdout
        assert (tmp_path / ".env").exists()
    finally:
        os.chdir(old_cwd)

def test_init_command_missing_env(tmp_path):
    import os
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        # Create dummy structure
        (tmp_path / "backend").mkdir()
        (tmp_path / "backend" / "manage.py").write_text("django")
        (tmp_path / "frontend").mkdir()
        (tmp_path / "frontend" / "package.json").write_text("{}")
        
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 1
        assert "No .env files found" in result.stdout
        assert "Run 'deployfilegen template'" in result.stdout
    finally:
        os.chdir(old_cwd)
