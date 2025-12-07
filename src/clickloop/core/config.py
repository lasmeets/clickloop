"""Configuration loading and validation."""

import json
import logging

logger = logging.getLogger("clickloop")


def load_config(config_path):
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to the JSON configuration file.

    Returns:
        dict: Configuration dictionary with defaults applied.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        json.JSONDecodeError: If config file is invalid JSON.
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        ) from exc
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
    config = {}

    if merge:
        try:
            config = load_config(config_path)
        except FileNotFoundError:
            # File doesn't exist, will create new one
            config = {
                "loops": 3,
                "wait_between_clicks": 1.0,
                "wait_between_loops": 2.0,
                "coordinates": [],
            }
        except (ValueError, json.JSONDecodeError) as exc:
            # File exists but is empty or has invalid JSON - treat as new file
            # Check if it's just an empty file (JSONDecodeError) vs truly invalid JSON
            # load_config wraps JSONDecodeError in ValueError, so check the original exception
            original_exc = exc.__cause__ if hasattr(exc, "__cause__") and exc.__cause__ else exc
            if isinstance(original_exc, json.JSONDecodeError) and original_exc.msg == "Expecting value":
                # Empty file - treat as new file
                config = {
                    "loops": 3,
                    "wait_between_clicks": 1.0,
                    "wait_between_loops": 2.0,
                    "coordinates": [],
                }
            else:
                # Truly invalid JSON - re-raise
                raise ValueError(f"Invalid JSON in configuration file: {exc}") from exc

    # Merge coordinates
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
