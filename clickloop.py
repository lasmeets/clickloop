#!/usr/bin/env python3
"""
ClickLoop - A simple script to automate mouse clicks at specified coordinates.

Uses Windows API via ctypes (standard library) to perform mouse clicks.
No external dependencies required.
"""

import sys
import time
import argparse
import json
from pathlib import Path
from ctypes import windll, Structure, c_long, byref


class POINT(Structure):
    """Windows POINT structure for coordinates."""
    _fields_ = [("x", c_long), ("y", c_long)]


def get_cursor_pos():
    """Get current cursor position."""
    point = POINT()
    windll.user32.GetCursorPos(byref(point))
    return (point.x, point.y)


def set_cursor_pos(x, y):
    """Set cursor position to (x, y)."""
    windll.user32.SetCursorPos(x, y)


def click_at(x, y, button="left"):
    """Click at specified coordinates."""
    set_cursor_pos(x, y)
    time.sleep(0.05)  # Small delay to ensure cursor moved

    if button == "left":
        windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
        windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
    elif button == "right":
        windll.user32.mouse_event(0x0008, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTDOWN
        windll.user32.mouse_event(0x0010, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTUP
    else:
        raise ValueError(f"Unsupported button: {button}. Use 'left' or 'right'")


def parse_coordinates(coords_str):
    """Parse coordinate string into list of (x, y) tuples.
    
    Expected format: "x1,y1 x2,y2 x3,y3" or "x1,y1;x2,y2;x3,y3"
    """
    if not coords_str:
        return []

    # Support both space and semicolon separators
    coords_str = coords_str.replace(";", " ")
    parts = coords_str.split()

    coordinates = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        try:
            x_str, y_str = part.split(",")
            x = int(x_str.strip())
            y = int(y_str.strip())
            coordinates.append((x, y))
        except ValueError as e:
            raise ValueError(
                f"Invalid coordinate format: '{part}'. Expected 'x,y'"
            ) from e

    return coordinates


def load_coordinates_from_file(filepath):
    """Load coordinates from a JSON file.
    
    Expected format: {"coordinates": [[x1, y1], [x2, y2], ...]}
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "coordinates" not in data:
        raise ValueError("Config file must contain 'coordinates' key")

    coords = data["coordinates"]
    if not isinstance(coords, list):
        raise ValueError("'coordinates' must be a list")

    result = []
    for i, coord in enumerate(coords):
        if not isinstance(coord, (list, tuple)) or len(coord) != 2:
            raise ValueError(
                f"Coordinate {i} must be a list/tuple of 2 numbers: {coord}"
            )

        try:
            x = int(coord[0])
            y = int(coord[1])
            result.append((x, y))
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Coordinate {i} contains non-numeric values: {coord}"
            ) from e

    return result


def run_click_loop(
    coordinates,
    loops=10,
    delay_between_clicks=1.0,
    delay_between_loops=2.0,
    button="left"
):
    """Run the click loop for specified number of iterations."""
    if not coordinates:
        print("No coordinates provided. Nothing to do.")
        return

    if loops <= 0:
        print("Loop count must be positive.")
        return

    print(f"Starting click loop: {loops} iterations")
    print(f"Coordinates: {coordinates}")
    print(f"Delay between clicks: {delay_between_clicks}s")
    print(f"Delay between loops: {delay_between_loops}s")
    print(f"Button: {button}")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    for loop_num in range(1, loops + 1):
        print(f"\n--- Loop {loop_num}/{loops} ---")

        for i, (x, y) in enumerate(coordinates, 1):
            print(f"Click {i}/{len(coordinates)}: ({x}, {y})")
            click_at(x, y, button=button)

            if i < len(coordinates):
                time.sleep(delay_between_clicks)

        if loop_num < loops:
            print(f"Waiting {delay_between_loops}s before next loop...")
            time.sleep(delay_between_loops)

    print("\n--- Click loop completed ---")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automate mouse clicks at specified coordinates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Click at (100, 200) then (300, 400), 10 times
  python clickloop.py -c "100,200 300,400"

  # Click 5 times with custom delays
  python clickloop.py -c "100,200 300,400" -l 5 -d 0.5 -D 1.0

  # Load coordinates from config file
  python clickloop.py -f config.json

  # Right-click instead of left-click
  python clickloop.py -c "100,200" --button right
        """
    )

    parser.add_argument(
        "-c", "--coordinates",
        type=str,
        help="Coordinates as string: 'x1,y1 x2,y2' or 'x1,y1;x2,y2'"
    )

    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Path to JSON config file with coordinates"
    )

    parser.add_argument(
        "-l", "--loops",
        type=int,
        default=10,
        help="Number of times to repeat the click sequence (default: 10)"
    )

    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between clicks (default: 1.0)"
    )

    parser.add_argument(
        "-D", "--delay-loops",
        type=float,
        default=2.0,
        help="Delay in seconds between loop iterations (default: 2.0)"
    )

    parser.add_argument(
        "--button",
        type=str,
        choices=["left", "right"],
        default="left",
        help="Mouse button to use (default: left)"
    )

    args = parser.parse_args()

    # Validate that coordinates are provided
    if not args.coordinates and not args.file:
        parser.error("Must provide either --coordinates (-c) or --file (-f)")

    if args.coordinates and args.file:
        parser.error("Cannot use both --coordinates and --file. Choose one.")

    # Load coordinates
    try:
        if args.file:
            coordinates = load_coordinates_from_file(args.file)
        else:
            coordinates = parse_coordinates(args.coordinates)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error loading coordinates: {e}", file=sys.stderr)
        sys.exit(1)

    if not coordinates:
        print("Error: No valid coordinates found.", file=sys.stderr)
        sys.exit(1)

    # Validate numeric arguments
    if args.loops < 1:
        print("Error: --loops must be at least 1", file=sys.stderr)
        sys.exit(1)

    if args.delay < 0:
        print("Error: --delay cannot be negative", file=sys.stderr)
        sys.exit(1)

    if args.delay_loops < 0:
        print("Error: --delay-loops cannot be negative", file=sys.stderr)
        sys.exit(1)

    # Run the click loop
    try:
        run_click_loop(
            coordinates=coordinates,
            loops=args.loops,
            delay_between_clicks=args.delay,
            delay_between_loops=args.delay_loops,
            button=args.button
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
