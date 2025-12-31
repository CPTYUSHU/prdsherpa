"""
Logging configuration for the application.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    # Create logs directory if needed
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Define log format
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Add file handler if log_file specified
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter(log_format, datefmt=date_format)
        )
        logging.getLogger().addHandler(file_handler)
    
    # Set specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # Too verbose in INFO
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={log_level}, file={log_file}")
    
    return logger


class RequestLogger:
    """Middleware for logging HTTP requests."""
    
    @staticmethod
    def log_request(method: str, path: str, status_code: int, duration_ms: float):
        """Log HTTP request details."""
        logger = logging.getLogger("api.request")
        
        # Color code by status
        if status_code < 300:
            level = logging.INFO
            status_emoji = "✅"
        elif status_code < 400:
            level = logging.INFO
            status_emoji = "↩️"
        elif status_code < 500:
            level = logging.WARNING
            status_emoji = "⚠️"
        else:
            level = logging.ERROR
            status_emoji = "❌"
        
        logger.log(
            level,
            f"{status_emoji} {method} {path} → {status_code} ({duration_ms:.2f}ms)"
        )
    
    @staticmethod
    def log_error(method: str, path: str, error: Exception):
        """Log HTTP request error."""
        logger = logging.getLogger("api.error")
        logger.error(
            f"❌ {method} {path} → ERROR: {type(error).__name__}: {str(error)}",
            exc_info=True
        )

