import os
from pathlib import Path
from typing import Optional
from deployfilegen.utils.logger import logger
from deployfilegen.exceptions import GenerationError

class FileWriter:
    """
    Handles file writing with safety checks (overwrite protection)
    and automatic directory creation.
    """
    
    def __init__(self, force: bool = False):
        self.force = force

    def write(self, path: Path, content: str) -> None:
        """
        Writes content to path.
        
        Args:
            path: Path object or string to the target file.
            content: String content to write.
        
        Raises:
            GenerationError: If write fails (permission, etc.)
        """
        target_path = Path(path)
        
        # Ensure parent directory exists
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise GenerationError(f"Failed to create directory {target_path.parent}: {e}")

        # Check if file exists
        if target_path.exists():
            if not self.force:
                return False
            else:
                logger.warning(f"OVERWRITE: {target_path}")
        else:
            logger.info(f"CREATE: {target_path}")

        # Write file
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except OSError as e:
            raise GenerationError(f"Failed to write to {target_path}: {e}")
