import logging
import sys

def setup_logger(name: str = "deployfilegen") -> logging.Logger:
    """Sets up a logger with a clean format for CLI usage."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()
