"""
Logging configuration for MindGarden.
"""

import sys
import logging
from pathlib import Path

from loguru import logger

from mindgarden.config.settings import get_config


class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to loguru."""

    def emit(self, record):
        """Intercept and emit logs."""
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    """Configure logging for MindGarden."""
    config = get_config()
    logs_dir = config.logs_dir
    
    # Create logs directory if it doesn't exist
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove any pre-existing loguru handlers
    logger.remove()
    
    # Setup loguru handler for console output
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    
    # Setup loguru handler for file output
    logger.add(
        logs_dir / "mindgarden.log",
        rotation="10 MB",
        retention="1 week",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # Replace standard library handlers with Loguru
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = [InterceptHandler()]
    
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    
    return logger 