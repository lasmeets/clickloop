"""Run command - executes the click loop."""

import time
import logging

from clickloop.core import (
    click_at,
    convert_to_virtual_coords,
    get_monitors,
    load_config,
    print_monitor_info,
    validate_config,
)

logger = logging.getLogger("clickloop")


def run_click_loop(config, monitors):
    """
    Execute the click loop with the given configuration.

    Args:
        config: Configuration dictionary.
        monitors: List of MonitorInfo objects.

    Raises:
        ValueError: If coordinates are invalid.
        RuntimeError: If clicking fails.
    """
    loops = config["loops"]
    wait_between_clicks = config["wait_between_clicks"]
    wait_between_loops = config["wait_between_loops"]
    coordinates = config["coordinates"]

    logger.info("Starting click loop: %s iterations", loops)
    logger.info("Coordinates to click: %s", len(coordinates))
    logger.info("Wait between clicks: %ss", wait_between_clicks)
    logger.info("Wait between loops: %ss", wait_between_loops)

    # Convert all coordinates to virtual coordinates upfront
    virtual_coords = []
    for coord in coordinates:
        virtual_x, virtual_y = convert_to_virtual_coords(
            coord["monitor"], coord["x"], coord["y"], monitors
        )
        virtual_coords.append((virtual_x, virtual_y))

    skipped_clicks = 0

    for loop_num in range(1, loops + 1):
        logger.info("Loop %s/%s", loop_num, loops)

        for coord_idx, (virtual_x, virtual_y) in enumerate(virtual_coords):
            coord = coordinates[coord_idx]
            logger.debug(
                "Clicking monitor %s at (%s, %s) [virtual: (%s, %s)]",
                coord["monitor"], coord["x"], coord["y"], virtual_x, virtual_y
            )

            try:
                click_at(virtual_x, virtual_y)
            except RuntimeError as e:
                logger.error(
                    "Failed to click at (%s, %s) after retries. Skipping this click. Error: %s",
                    virtual_x, virtual_y, str(e)
                )
                skipped_clicks += 1

            if coord_idx < len(virtual_coords) - 1 and wait_between_clicks > 0:
                time.sleep(wait_between_clicks)

        if loop_num < loops:
            logger.debug("Waiting %ss before next loop...", wait_between_loops)
            time.sleep(wait_between_loops)

    logger.info("Click loop completed!")


def run_command(args):
    """
    Execute the run command.

    Args:
        args: Parsed command-line arguments.

    Raises:
        FileNotFoundError: If configuration file is not found.
        ValueError: If configuration is invalid.
        RuntimeError: If monitor detection or clicking fails.
    """
    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        logger.warning("Configuration file '%s' not found. Using defaults.", args.config)
        raise FileNotFoundError(f"Configuration file not found: {args.config}") from e

    # Override with CLI arguments
    if args.loops is not None:
        config["loops"] = args.loops

    if args.wait_clicks is not None:
        config["wait_between_clicks"] = args.wait_clicks

    if args.wait_loops is not None:
        config["wait_between_loops"] = args.wait_loops

    # Validate configuration
    try:
        validate_config(config)
    except ValueError as e:
        logger.error("Invalid configuration: %s", e)
        raise ValueError(f"Invalid configuration: {e}") from e

    # Detect monitors
    monitors = get_monitors()

    if len(monitors) == 0:
        logger.error("No monitors detected")
        raise RuntimeError("No monitors detected")

    print_monitor_info(monitors)

    # Validate coordinates against monitors
    if len(config["coordinates"]) == 0:
        logger.error("No coordinates specified in configuration")
        raise ValueError("No coordinates specified in configuration")

    for coord in config["coordinates"]:
        convert_to_virtual_coords(
            coord["monitor"], coord["x"], coord["y"], monitors
        )

    # Run the click loop
    run_click_loop(config, monitors)
