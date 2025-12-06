"""Logging configuration for ClickLoop."""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level=logging.INFO):
    """
    Setup logging configuration for ClickLoop.

    Creates the log directory if it doesn't exist and configures both
    file and console handlers. Console output is less verbose, while
    file logs include detailed timestamps and context.

    Args:
        log_level: Logging level (default: logging.INFO)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger("clickloop")
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler - less verbose output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)

    # File handler - detailed format with timestamps
    log_file = log_dir / "clickloop.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=2_000_000, backupCount=2, encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    )
    logger.addHandler(file_handler)

    return logger

