import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict

from deployfilegen.exceptions import EnvConfigError
from deployfilegen.utils.logger import logger

REQUIRED_ENV_VARS = [
    "DOCKER_USERNAME",
    "BACKEND_IMAGE_NAME",
    "FRONTEND_IMAGE_NAME",
    "DEPLOY_HOST",
    "DEPLOY_USER",
]

def load_environment(project_root: Path) -> None:
    """
    Loads .env files in layered order:
    1. project-root/.env
    2. backend/.env
    3. frontend/.env
    
    Later files override earlier ones.
    """
    env_files = [
        project_root / ".env",
        project_root / "backend" / ".env",
        project_root / "frontend" / ".env",
    ]
    
    loaded = False
    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file, override=True)
            logger.info(f"Loaded environment from: {env_file}")
            loaded = True
            
    if not loaded:
        raise EnvConfigError("No .env files found in likely locations.")

def validate_environment() -> Dict[str, str]:
    """
    Validates that all required environment variables are set.
    Returns a dictionary of the variables.
    """
    missing = []
    config = {}
    
    for var in REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            config[var] = value
            
    if missing:
        raise EnvConfigError(f"Missing required environment variables: {', '.join(missing)}")
        
    return config
