"""Tests for deploy strategy separation (v0.1.31)."""
import os
from unittest.mock import patch
from deployfilegen.config.env_loader import validate_environment
from deployfilegen.generators.github import generate_github_workflow
from deployfilegen.generators.compose import generate_docker_compose


# ─── VALIDATION TESTS ─────────────────────────────────────────

class TestValidation:
    """Validation layer only checks vars based on deploy strategy."""

    @patch.dict(os.environ, {"DEPLOY_HOST": "1.2.3.4", "DEPLOY_USER": "ubuntu"}, clear=True)
    def test_ssh_mode_needs_only_ssh_vars(self):
        """SSH deploy should NOT require registry variables."""
        config = validate_environment(mode="prod", deploy="ssh")
        assert config["DEPLOY_HOST"] == "1.2.3.4"
        assert config["DEPLOY_USER"] == "ubuntu"
        # Registry vars should get defaults, not crash
        assert config["BACKEND_IMAGE_NAME"] == "backend"

    @patch.dict(os.environ, {"DEPLOY_HOST": "1.2.3.4", "DEPLOY_USER": "ubuntu"}, clear=True)
    def test_registry_mode_fails_without_registry_vars(self):
        """Registry deploy MUST require registry variables."""
        try:
            validate_environment(mode="prod", deploy="registry")
            assert False, "Should have raised EnvConfigError"
        except Exception as e:
            assert "DOCKER_USERNAME" in str(e)

    @patch.dict(os.environ, {
        "DEPLOY_HOST": "1.2.3.4", "DEPLOY_USER": "ubuntu",
        "DOCKER_USERNAME": "user", "BACKEND_IMAGE_NAME": "user/be", "FRONTEND_IMAGE_NAME": "user/fe",
    }, clear=True)
    def test_registry_mode_passes_with_all_vars(self):
        """Registry deploy should pass when all vars are present."""
        config = validate_environment(mode="prod", deploy="registry")
        assert config["DOCKER_USERNAME"] == "user"
        assert config["BACKEND_IMAGE_NAME"] == "user/be"

    @patch.dict(os.environ, {}, clear=True)
    def test_dev_mode_has_no_requirements(self):
        """Dev mode should never require any vars."""
        config = validate_environment(mode="dev", deploy="ssh")
        assert "BACKEND_IMAGE_NAME" in config  # defaults provided


# ─── WORKFLOW TESTS ────────────────────────────────────────────

class TestWorkflows:
    """Workflow generator produces strategy-specific output."""

    def test_ssh_workflow_has_git_pull(self):
        workflow = generate_github_workflow({}, deploy="ssh")
        assert "git pull" in workflow
        assert "docker compose" in workflow
        assert "Docker Hub" not in workflow  # No registry steps

    def test_registry_workflow_has_push(self):
        workflow = generate_github_workflow({}, deploy="registry")
        assert "Docker Hub" in workflow
        assert "Build and Push" in workflow
        assert "docker compose" in workflow


# ─── COMPOSE TESTS ─────────────────────────────────────────────

class TestCompose:
    """Compose generator uses build: for SSH, image: for registry."""

    def test_ssh_prod_compose_uses_build(self):
        compose = generate_docker_compose("prod", {}, deploy="ssh")
        assert "build:" in compose
        assert "context: ./backend" in compose
        assert "${BACKEND_IMAGE_NAME}" not in compose

    def test_registry_prod_compose_uses_image(self):
        compose = generate_docker_compose("prod", {}, deploy="registry")
        assert "${BACKEND_IMAGE_NAME}" in compose
        assert "context: ./backend" not in compose

    def test_dev_compose_always_uses_build(self):
        compose = generate_docker_compose("dev", {}, deploy="ssh")
        assert "build:" in compose
        compose2 = generate_docker_compose("dev", {}, deploy="registry")
        assert "build:" in compose2  # dev mode ignores deploy strategy
