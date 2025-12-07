#!/usr/bin/env python3
"""
ClickLoop - Automated mouse clicking script for Windows with multi-monitor support.

Uses only Python standard library (ctypes for Windows API).
"""

import argparse

from clickloop.commands import pick_command, run_command
from clickloop.utils.logging import setup_logging


def main():
    """Main entry point."""
    # Initialize logging
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Automated mouse clicking script with multi-monitor support"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    # Run command (default behavior)
    run_parser = subparsers.add_parser(
        "run",
        help="Run the click loop (default command)",
        description="Execute automated clicking based on configuration file",
    )
    run_parser.add_argument(
        "--config",
        type=str,
        default="data/config/coordinates.json",
        help="Path to configuration file (default: data/config/coordinates.json)",
    )
    run_parser.add_argument(
        "--loops",
        type=int,
        help="Number of loop iterations (overrides config)",
    )
    run_parser.add_argument(
        "--wait-clicks",
        type=float,
        dest="wait_clicks",
        help="Wait time between clicks in seconds (overrides config)",
    )
    run_parser.add_argument(
        "--wait-loops",
        type=float,
        dest="wait_loops",
        help="Wait time between loops in seconds (overrides config)",
    )
    run_parser.set_defaults(func=run_command)

    # Pick command
    pick_parser = subparsers.add_parser(
        "pick",
        help="Interactive coordinate picker",
        description="Interactive tool to find and capture XY coordinates",
    )
    pick_parser.add_argument(
        "--config",
        type=str,
        default="data/config/coordinates.json",
        help="Path to configuration file to save coordinates (default: data/config/coordinates.json)",
    )
    pick_parser.set_defaults(func=pick_command)

    args = parser.parse_args()

    # Execute the appropriate command
    args.func(args)


if __name__ == "__main__":
    main()
