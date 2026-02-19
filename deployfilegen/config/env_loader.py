import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict

from deployfilegen.exceptions import EnvConfigError
from deployfilegen.utils.logger import logger

# Deploy-strategy-aware variable requirements
SSH_REQUIRED_VARS = [
    "DEPLOY_HOST",
    "DEPLOY_USER",
]

REGISTRY_REQUIRED_VARS = SSH_REQUIRED_VARS + [
    "DOCKER_USERNAME",
    "BACKEND_IMAGE_NAME",
    "FRONTEND_IMAGE_NAME",
]


def load_environment(project_root: Path) -> List[Path]:
    """
    Loads .env files in layered order:
    1. project-root/.env
    2. backend/.env
    3. frontend/.env
    
    Later files override earlier ones.
    Returns a list of .env file paths that were found and loaded.
    """
    env_files = [
        project_root / ".env",
        project_root / "backend" / ".env",
        project_root / "frontend" / ".env",
    ]
    
    loaded_files = []
    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file, override=True)
            logger.info(f"Loaded environment from: {env_file}")
            loaded_files.append(env_file)
            
    if not loaded_files:
        raise EnvConfigError("No .env files found in likely locations.")
    
    return loaded_files


def validate_environment(mode: str = "prod", deploy: str = "ssh") -> Dict[str, str]:
    """
    Validates that required environment variables are set.
    
    - dev mode: no deployment variables required.
    - prod mode + ssh deploy: only DEPLOY_HOST, DEPLOY_USER required.
    - prod mode + registry deploy: SSH vars + DOCKER_USERNAME, IMAGE_NAMEs required.
    
    Returns a dictionary of the variables found.
    """
    config = {}
    
    if mode == "dev":
        # Dev mode: no strict requirements. Collect whatever is available.
        for var in REGISTRY_REQUIRED_VARS:
            value = os.getenv(var)
            if value:
                config[var] = value
        
        config.setdefault("BACKEND_IMAGE_NAME", "backend")
        config.setdefault("FRONTEND_IMAGE_NAME", "frontend")
        return config
    
    # Prod mode: validate based on deploy strategy
    required_vars = REGISTRY_REQUIRED_VARS if deploy == "registry" else SSH_REQUIRED_VARS
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            config[var] = value
    
    if missing:
        strategy_label = "registry" if deploy == "registry" else "SSH"
        raise EnvConfigError(
            f"Missing required variables for {strategy_label} deployment: {', '.join(missing)}"
        )
    
    # Provide defaults for non-required vars (SSH mode doesn't need image names)
    config.setdefault("BACKEND_IMAGE_NAME", "backend")
    config.setdefault("FRONTEND_IMAGE_NAME", "frontend")
        
    return config
