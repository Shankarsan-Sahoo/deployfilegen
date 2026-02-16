class DeployFileGenError(Exception):
    """Base exception for deployfilegen."""
    pass

class ProjectStructureError(DeployFileGenError):
    """Raised when project structure is invalid (missing backend/frontend)."""
    pass

class DetectionError(DeployFileGenError):
    """Raised when framework detection fails."""
    pass

class EnvConfigError(DeployFileGenError):
    """Raised when .env configuration is missing or invalid."""
    pass

class GenerationError(DeployFileGenError):
    """Raised when file generation fails."""
    pass
