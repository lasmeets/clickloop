"""Pick command - interactive coordinate picker."""

import ctypes
import logging
import sys
import time
from ctypes import POINTER, Structure, c_int, c_long, windll
from ctypes.wintypes import BOOL

from clickloop.core import (
    get_monitor_for_point,
    get_monitors,
    save_coordinates_to_config,
)

logger = logging.getLogger("clickloop")

# Windows API structures
class POINT(Structure):  # pylint: disable=too-few-public-methods
    """A point on a screen."""

    _fields_ = [("x", c_long), ("y", c_long)]


# Windows API function prototypes
user32 = windll.user32

# Set up GetCursorPos function prototype
user32.GetCursorPos.argtypes = [POINTER(POINT)]
user32.GetCursorPos.restype = BOOL

# Set up GetAsyncKeyState function prototype
user32.GetAsyncKeyState.argtypes = [c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short

# Virtual key codes
VK_SPACE = 0x20
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_LBUTTON = 0x01


def pick_coordinates(config_path=None):
    """
    Interactive coordinate picker that tracks mouse position and captures coordinates.

    Args:
        config_path: Optional path to config file. If None, will prompt or use default.

    Raises:
        RuntimeError: If monitor detection fails or Windows API calls fail.
        KeyboardInterrupt: If user presses Ctrl+C or Esc.
    """
    # Detect monitors
    try:
        monitors = get_monitors()
    except RuntimeError as e:
        raise RuntimeError(f"Failed to detect monitors: {e}") from e

    if len(monitors) == 0:
        raise RuntimeError("No monitors detected")

    print("\n" + "=" * 60)
    print("Coordinate Picker Mode")
    print("=" * 60)
    print("\nDetected monitors:")
    for idx, monitor in enumerate(monitors):
        primary_str = " (PRIMARY)" if monitor.is_primary else ""
        print(
            f"  Monitor {idx}: {monitor.width}x{monitor.height} "
            f"at ({monitor.left}, {monitor.top}){primary_str}"
        )

    print("\n" + "-" * 60)
    print("Instructions:")
    print("  - Move your mouse to the desired position")
    print("  - Press SPACE or ENTER to capture current position")
    print("  - Click LEFT MOUSE BUTTON to capture current position")
    print("  - Press ESC to finish and save coordinates")
    print("  - Press Ctrl+C to exit without saving")
    print("-" * 60 + "\n")

    captured_coords = []
    last_key_state = {"space": False, "enter": False, "escape": False}
    last_mouse_state = False

    try:
        while True:
            # Get current mouse position
            point = POINT()
            if not user32.GetCursorPos(ctypes.byref(point)):
                time.sleep(0.01)
                continue

            virtual_x = point.x
            virtual_y = point.y

            # Find which monitor contains this point
            monitor_idx, monitor = get_monitor_for_point(virtual_x, virtual_y, monitors)

            if monitor_idx == -1:
                # Mouse is outside all monitors
                monitor_relative_x = virtual_x
                monitor_relative_y = virtual_y
                monitor_info = "OUTSIDE"
            else:
                monitor_relative_x = virtual_x - monitor.left
                monitor_relative_y = virtual_y - monitor.top
                monitor_info = f"Monitor {monitor_idx}"

            # Check keyboard state
            space_pressed = (user32.GetAsyncKeyState(VK_SPACE) & 0x8000) != 0
            enter_pressed = (user32.GetAsyncKeyState(VK_RETURN) & 0x8000) != 0
            escape_pressed = (user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000) != 0
            mouse_pressed = (user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000) != 0

            # Detect key press (transition from not pressed to pressed)
            if (space_pressed or enter_pressed or mouse_pressed) and not (
                last_key_state["space"] or last_key_state["enter"] or last_mouse_state
            ):
                if monitor_idx == -1:
                    print("\n⚠ Warning: Mouse is outside all monitors, coordinate may be invalid")

                coord = {
                    "monitor": monitor_idx if monitor_idx != -1 else 0,
                    "x": int(monitor_relative_x),
                    "y": int(monitor_relative_y),
                }
                captured_coords.append(coord)
                print(
                    f"\n✓ Captured coordinate #{len(captured_coords)}: "
                    f"Monitor {coord['monitor']}, ({coord['x']}, {coord['y']}) "
                    f"[Virtual: ({virtual_x}, {virtual_y})]"
                )

            # Check for escape to finish
            if escape_pressed and not last_key_state["escape"]:
                break

            # Update last states
            last_key_state["space"] = space_pressed
            last_key_state["enter"] = enter_pressed
            last_key_state["escape"] = escape_pressed
            last_mouse_state = mouse_pressed

            # Display current position (clear and redraw)
            print(
                f"\rCurrent: {monitor_info} | "
                f"Monitor-relative: ({monitor_relative_x}, {monitor_relative_y}) | "
                f"Virtual: ({virtual_x}, {virtual_y}) | "
                f"Captured: {len(captured_coords)}",
                end="",
                flush=True,
            )

            time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting without saving.")
        return

    print("\n\n" + "=" * 60)
    print(f"Capture complete! Captured {len(captured_coords)} coordinate(s).")

    if len(captured_coords) == 0:
        print("No coordinates to save.")
        return

    # Display captured coordinates
    print("\nCaptured coordinates:")
    for i, coord in enumerate(captured_coords, 1):
        print(f"  {i}. Monitor {coord['monitor']}: ({coord['x']}, {coord['y']})")

    # Determine config file path
    if config_path is None:
        default_path = "data/config/coordinates.json"
        try:
            response = input(
                f"\nSave to config file? [Enter for default '{default_path}', "
                "or type path, or 'n' to skip]: "
            ).strip()

            if response.lower() == "n":
                print("Skipping save. Coordinates printed above.")
                return

            config_path = response if response else default_path
        except (EOFError, KeyboardInterrupt):
            print("\nSkipping save.")
            return

    # Save to config file
    try:
        save_coordinates_to_config(captured_coords, config_path, merge=True)
        print(f"\n✓ Successfully saved {len(captured_coords)} coordinate(s) to {config_path}")
    except (ValueError, OSError) as e:
        print(f"\n✗ Error saving coordinates: {e}")
        raise


def pick_command(args):
    """
    Execute the pick command.

    Args:
        args: Parsed command-line arguments.

    Raises:
        SystemExit: On error or completion.
    """
    try:
        pick_coordinates(args.config)
    except (RuntimeError, ValueError, OSError) as e:
        logger.error("Error in coordinate picker: %s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Coordinate picker interrupted by user")
        sys.exit(0)

