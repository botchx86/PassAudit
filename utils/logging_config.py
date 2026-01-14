"""
Logging Configuration
Centralized logging setup for PassAudit
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = False,
    log_dir: Optional[str] = None
) -> logging.Logger:
    """
    Setup centralized logging for PassAudit

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        log_dir: Directory for log files (default: ~/.passaudit/logs/)

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger('passaudit')
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if log_to_file:
        if log_dir is None:
            log_dir = str(Path.home() / ".passaudit" / "logs")

        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "passaudit.log")

        # Rotating file handler (10MB per file, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger instance

    Args:
        name: Logger name (default: 'passaudit')

    Returns:
        Logger instance
    """
    if name is None:
        return logging.getLogger('passaudit')
    return logging.getLogger(f'passaudit.{name}')


# Initialize default logger
_default_logger = None


def init_default_logger(config: dict = None):
    """
    Initialize default logger from configuration

    Args:
        config: Configuration dictionary
    """
    global _default_logger

    if config is None:
        config = {}

    logging_config = config.get('logging', {})

    level = logging_config.get('level', 'INFO')
    log_to_file = logging_config.get('file_output', True)
    log_to_console = logging_config.get('console_output', False)

    _default_logger = setup_logging(
        level=level,
        log_to_file=log_to_file,
        log_to_console=log_to_console
    )

    return _default_logger


def log_analysis_start(password_count: int, check_hibp: bool = False):
    """Log analysis start"""
    logger = get_logger()
    logger.info(
        f"Starting analysis of {password_count} password(s) "
        f"(HIBP: {'enabled' if check_hibp else 'disabled'})"
    )


def log_analysis_complete(password_count: int, duration: float):
    """Log analysis completion"""
    logger = get_logger()
    logger.info(
        f"Analysis complete: {password_count} password(s) "
        f"in {duration:.2f}s ({password_count/duration:.1f} passwords/sec)"
    )


def log_hibp_check(password_length: int, is_pwned: bool, cached: bool = False):
    """Log HIBP check"""
    logger = get_logger('hibp')
    cache_status = " (cached)" if cached else ""
    status = "FOUND IN BREACHES" if is_pwned else "not found"
    logger.debug(
        f"HIBP check for {password_length}-char password: {status}{cache_status}"
    )


def log_error(operation: str, error: Exception):
    """Log error"""
    logger = get_logger()
    logger.error(f"Error during {operation}: {str(error)}", exc_info=True)


def log_warning(message: str):
    """Log warning"""
    logger = get_logger()
    logger.warning(message)


def log_info(message: str):
    """Log info"""
    logger = get_logger()
    logger.info(message)


def log_debug(message: str):
    """Log debug"""
    logger = get_logger()
    logger.debug(message)
