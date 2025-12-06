"""Logging configuration for ClickLoop."""

import logging
from pathlib import Path


def setup_logging(log_level=logging.INFO):
    """
    Setup logging configuration for ClickLoop.

    Creates the log directory if it doesn't exist and configures both
    file and console handlers with detailed formatting.

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

    # Detailed format: timestamp, level, module, message
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler - write to data/logs/clickloop.log
    log_file = log_dir / "clickloop.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler - output to stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

