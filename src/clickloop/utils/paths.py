"""Path utilities for resolving package data directories."""

from pathlib import Path


def get_package_data_dir():
    """
    Get the package data directory relative to the installed package.

    Returns the absolute path to the 'data' directory within the clickloop package,
    regardless of the current working directory. This ensures that when running the
    tool from any location, it always references the correct data folder.

    Returns:
        Path: Absolute path to the data directory.

    Raises:
        RuntimeError: If the data directory doesn't exist after resolution.
    """
    # Get the directory containing this file (src/clickloop/utils/)
    utils_dir = Path(__file__).parent

    # Navigate to package root: src/clickloop/utils -> src/clickloop -> src -> project root
    package_root = utils_dir.parent.parent.parent

    # Resolve to absolute path to handle symlinks and relative imports
    package_root = package_root.resolve()

    # Data directory should be at: project_root/data
    data_dir = package_root / "data"

    return data_dir


def get_package_config_dir():
    """
    Get the package config directory (data/config).

    Returns:
        Path: Absolute path to the config directory.
    """
    data_dir = get_package_data_dir()
    return data_dir / "config"


def get_package_logs_dir():
    """
    Get the package logs directory (data/logs).

    Returns:
        Path: Absolute path to the logs directory.
    """
    data_dir = get_package_data_dir()
    return data_dir / "logs"
