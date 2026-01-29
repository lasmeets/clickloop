"""Configuration loading and validation."""

import json
import shutil
import logging
from pathlib import Path

logger = logging.getLogger("clickloop")


def _try_copy_example_config(config_path):
    """
    Try to copy example config file if it exists.

    Args:
        config_path: Path to the desired config file.

    Returns:
        bool: True if example was copied, False otherwise.
    """
    example_path = Path(str(config_path) + ".example")

    if example_path.exists():
        try:
            config_dir = Path(config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(example_path), str(config_path))
            logger.info("Created config from example file: %s", config_path)
            return True
        except (OSError, shutil.Error) as exc:
            logger.warning(
                "Failed to copy example config from %s: %s",
                example_path, str(exc)
            )
            return False

    return False


def load_config(config_path):
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to the JSON configuration file.

    Returns:
        dict: Configuration dictionary with defaults applied.

    Raises:
        FileNotFoundError: If config file doesn't exist and example can't be copied.
        json.JSONDecodeError: If config file is invalid JSON.
    """
    config_path_obj = Path(config_path)

    if not config_path_obj.exists():
        if _try_copy_example_config(config_path):
            logger.info("Using example configuration")
        else:
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}. "
                f"No example file available to copy."
            )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in configuration file: {exc}") from exc

    # Apply defaults
    defaults = {
        "loops": 3,
        "wait_between_clicks": 1.0,
        "wait_between_loops": 2.0,
        "coordinates": [],
    }

    for key, default_value in defaults.items():
        if key not in config:
            config[key] = default_value

    return config


def _validate_coordinate(i, coord):
    if not isinstance(coord, dict):
        raise ValueError(f"Coordinate {i} must be a dictionary")

    if "monitor" not in coord:
        raise ValueError(f"Coordinate {i} missing 'monitor' field")

    if "x" not in coord:
        raise ValueError(f"Coordinate {i} missing 'x' field")

    if "y" not in coord:
        raise ValueError(f"Coordinate {i} missing 'y' field")

    monitor = coord["monitor"]
    if not isinstance(monitor, int) or monitor < 0:
        raise ValueError(
            f"Coordinate {i}: monitor must be a non-negative integer, got {monitor}"
        )

    x = coord["x"]
    if not isinstance(x, (int, float)) or x < 0:
        raise ValueError(
            f"Coordinate {i}: x must be a non-negative number, got {x}"
        )

    y = coord["y"]
    if not isinstance(y, (int, float)) or y < 0:
        raise ValueError(
            f"Coordinate {i}: y must be a non-negative number, got {y}"
        )


def validate_config(config):
    """
    Validate configuration values.

    Args:
        config: Configuration dictionary.

    Raises:
        ValueError: If configuration is invalid.
    """
    if "loops" in config:
        loops = config["loops"]
        if not isinstance(loops, int) or loops < 1:
            raise ValueError(f"loops must be a positive integer, got {loops}")

    if "wait_between_clicks" in config:
        wait = config["wait_between_clicks"]
        if not isinstance(wait, (int, float)) or wait < 0:
            raise ValueError(
                f"wait_between_clicks must be a non-negative number, got {wait}"
            )

    if "wait_between_loops" in config:
        wait = config["wait_between_loops"]
        if not isinstance(wait, (int, float)) or wait < 0:
            raise ValueError(
                f"wait_between_loops must be a non-negative number, got {wait}"
            )

    if "coordinates" not in config:
        raise ValueError("coordinates must be a list")

    if not isinstance(config["coordinates"], list):
        raise ValueError("coordinates must be a list")

    if len(config["coordinates"]) == 0:
        raise ValueError("At least one coordinate must be specified")

    for i, coord in enumerate(config["coordinates"]):
        _validate_coordinate(i, coord)


def _get_default_config():
    """Get default configuration dictionary."""
    return {
        "loops": 3,
        "wait_between_clicks": 1.0,
        "wait_between_loops": 2.0,
        "coordinates": [],
    }


def _load_existing_config(config_path):
    """
    Load existing config or return defaults if load fails.

    Args:
        config_path: Path to the configuration file.

    Returns:
        dict: Configuration dictionary.

    Raises:
        ValueError: If config file contains invalid JSON (not empty file).
    """
    try:
        return load_config(config_path)
    except FileNotFoundError:
        return _get_default_config()
    except ValueError as exc:
        # Check if it's just an empty file
        if "Expecting value" in str(exc):
            return _get_default_config()
        raise


def save_coordinates_to_config(coordinates, config_path, merge=True):
    """
    Save captured coordinates to configuration file.

    Args:
        coordinates: List of coordinate dictionaries to save.
        config_path: Path to the configuration file.
        merge: If True, merge with existing config. If False, create new config.

    Raises:
        ValueError: If config file exists and contains invalid JSON.
        OSError: If file cannot be written.
    """
    if merge:
        config = _load_existing_config(config_path)
    else:
        config = _get_default_config()

    # Ensure coordinates list exists
    if "coordinates" not in config:
        config["coordinates"] = []

    config["coordinates"].extend(coordinates)

    # Write to file
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError as exc:
        raise OSError(f"Failed to write configuration file: {exc}") from exc

    logger.info("Saved %s coordinate(s) to %s", len(coordinates), config_path)
