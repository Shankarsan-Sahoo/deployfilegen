from pathlib import Path
from deployfilegen.exceptions import DetectionError, ProjectStructureError
from deployfilegen.utils.logger import logger

def detect_django_backend(project_root: Path) -> Path:
    """
    Detects Django backend by checking for manage.py.
    Returns path to backend directory.
    """
    backend_path = project_root / "backend"
    manage_py = backend_path / "manage.py"
    
    if not backend_path.exists():
        raise ProjectStructureError(f"Backend directory not found at: {backend_path}")
        
    if not manage_py.exists():
        raise DetectionError(f"Django not detected: {manage_py} is missing.")
        
    logger.info("Detected Django backend.")
    return backend_path

def detect_react_frontend(project_root: Path) -> Path:
    """
    Detects React frontend by checking for package.json.
    Returns path to frontend directory.
    """
    frontend_path = project_root / "frontend"
    package_json = frontend_path / "package.json"
    
    if not frontend_path.exists():
        raise ProjectStructureError(f"Frontend directory not found at: {frontend_path}")
        
    if not package_json.exists():
        raise DetectionError(f"React not detected: {package_json} is missing.")
        
    logger.info("Detected React frontend.")
    return frontend_path
