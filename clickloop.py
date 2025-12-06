#!/usr/bin/env python3
"""
ClickLoop - Automated mouse clicking script for Windows with multi-monitor support.

Uses only Python standard library (ctypes for Windows API).
"""

import sys
import json
import time
import ctypes
import argparse
from ctypes import Structure, POINTER, c_uint, c_long, windll, WINFUNCTYPE
from ctypes.wintypes import BOOL, DWORD, HMONITOR, HDC, RECT, LPARAM


# Windows API structures and constants
class MONITORINFO(Structure):
    """Information about a display monitor."""
    _fields_ = [
        ("cbSize", DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", DWORD),
    ]


MONITORINFOF_PRIMARY = 1
MONITOR_DEFAULTTONULL = 0
MONITOR_DEFAULTTOPRIMARY = 1
MONITOR_DEFAULTTONEAREST = 2

# Mouse input constants
INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000


class POINT(Structure):
    """A point on a screen."""
    _fields_ = [("x", c_long), ("y", c_long)]


class MOUSEINPUT(Structure):
    """Mouse input information."""
    _fields_ = [
        ("dx", c_long),
        ("dy", c_long),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", POINTER(c_uint)),
    ]


class INPUT(Structure):
    """Input information."""
    class _INPUT(Structure):
        """Input information."""
        _fields_ = [("mi", MOUSEINPUT)]

    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", DWORD),
        ("_input", _INPUT),
    ]


# Windows API function prototypes
user32 = windll.user32
gdi32 = windll.gdi32

MonitorEnumProc = WINFUNCTYPE(BOOL, HMONITOR, HDC, POINTER(RECT), LPARAM)

# Set up GetMonitorInfoW function prototype
user32.GetMonitorInfoW.argtypes = [HMONITOR, POINTER(MONITORINFO)]
user32.GetMonitorInfoW.restype = BOOL


class MonitorInfo:
    """Information about a display monitor."""

    def __init__(self, handle, bounds, is_primary):
        self.handle = handle
        self.bounds = bounds
        self.is_primary = is_primary

    @property
    def left(self):
        """Get the left coordinate of the monitor."""
        return self.bounds.left

    @property
    def top(self):
        """Get the top coordinate of the monitor."""
        return self.bounds.top

    @property
    def right(self):
        """Get the right coordinate of the monitor."""
        return self.bounds.right

    @property
    def bottom(self):
        """Get the bottom coordinate of the monitor."""
        return self.bounds.bottom

    @property
    def width(self):
        """Get the width of the monitor."""
        return self.bounds.right - self.bounds.left

    @property
    def height(self):
        """Get the height of the monitor."""
        return self.bounds.bottom - self.bounds.top

    def __repr__(self):
        primary_str = " (PRIMARY)" if self.is_primary else ""
        return (
            f"Monitor({self.left}, {self.top}, "
            f"{self.right}, {self.bottom}){primary_str}"
        )


def get_monitors():
    """
    Enumerate all display monitors and return their information.

    Returns:
        list[MonitorInfo]: List of monitor information objects.

    Raises:
        RuntimeError: If monitor enumeration fails.
    """
    monitors = []

    def enum_proc(hmonitor, _hdc, _lprect, _lparam):
        info = MONITORINFO()
        info.cbSize = DWORD(ctypes.sizeof(MONITORINFO))  # pylint: disable=attribute-defined-outside-init
        if not user32.GetMonitorInfoW(hmonitor, ctypes.byref(info)):
            error_code = ctypes.get_last_error()
            if error_code != 0:
                print(
                    f"Warning: GetMonitorInfoW failed with error {error_code}",
                    file=sys.stderr
                )
            return True

        is_primary = bool(info.dwFlags & MONITORINFOF_PRIMARY)
        monitor = MonitorInfo(hmonitor, info.rcMonitor, is_primary)
        monitors.append(monitor)
        return True

    callback = MonitorEnumProc(enum_proc)
    if not user32.EnumDisplayMonitors(None, None, callback, 0):
        raise RuntimeError("Failed to enumerate display monitors")

    # Validate that we got valid monitor data
    if len(monitors) == 0:
        raise RuntimeError("No monitors detected")

    # Check if any monitors have invalid dimensions (fallback to alternative method)
    invalid_monitors = [
        m for m in monitors if m.width == 0 or m.height == 0
    ]
    if invalid_monitors:
        return get_monitors_alternative()

    return monitors


def get_monitors_alternative():
    """
    Alternative monitor detection using EnumDisplayDevices and EnumDisplaySettings.

    This is a fallback method when GetMonitorInfoW doesn't work correctly.

    Returns:
        list[MonitorInfo]: List of monitor information objects.

    Raises:
        RuntimeError: If monitor enumeration fails.
    """
    # Define structures needed for EnumDisplayDevices
    class DISPLAY_DEVICE(Structure):  # pylint: disable=invalid-name
        """Display device information."""
        _fields_ = [
            ("cb", DWORD),
            ("DeviceName", ctypes.c_wchar * 32),
            ("DeviceString", ctypes.c_wchar * 128),
            ("StateFlags", DWORD),
            ("DeviceID", ctypes.c_wchar * 128),
            ("DeviceKey", ctypes.c_wchar * 128),
        ]

    class DEVMODE(Structure):  # pylint: disable=invalid-name
        """Device mode information."""
        _fields_ = [
            ("dmDeviceName", ctypes.c_wchar * 32),
            ("dmSpecVersion", ctypes.c_ushort),
            ("dmDriverVersion", ctypes.c_ushort),
            ("dmSize", ctypes.c_ushort),
            ("dmDriverExtra", ctypes.c_ushort),
            ("dmFields", DWORD),
            ("dmOrientation", ctypes.c_short),
            ("dmPaperSize", ctypes.c_short),
            ("dmPaperLength", ctypes.c_short),
            ("dmPaperWidth", ctypes.c_short),
            ("dmScale", ctypes.c_short),
            ("dmCopies", ctypes.c_short),
            ("dmDefaultSource", ctypes.c_short),
            ("dmPrintQuality", ctypes.c_short),
            ("dmColor", ctypes.c_short),
            ("dmDuplex", ctypes.c_short),
            ("dmYResolution", ctypes.c_short),
            ("dmTTOption", ctypes.c_short),
            ("dmCollate", ctypes.c_short),
            ("dmFormName", ctypes.c_wchar * 32),
            ("dmLogPixels", ctypes.c_ushort),
            ("dmBitsPerPel", DWORD),
            ("dmPelsWidth", DWORD),
            ("dmPelsHeight", DWORD),
            ("dmDisplayFlags", DWORD),
            ("dmDisplayFrequency", DWORD),
        ]

    ENUM_CURRENT_SETTINGS = -1

    # Set up function prototypes
    user32.EnumDisplayDevicesW.argtypes = [
        ctypes.c_wchar_p, DWORD, POINTER(DISPLAY_DEVICE), DWORD
    ]
    user32.EnumDisplayDevicesW.restype = BOOL

    user32.EnumDisplaySettingsW.argtypes = [
        ctypes.c_wchar_p, DWORD, POINTER(DEVMODE)
    ]
    user32.EnumDisplaySettingsW.restype = BOOL

    monitors = []
    device_index = 0
    primary_found = False

    while True:
        device = DISPLAY_DEVICE()  # pylint: disable=attribute-defined-outside-init
        device.cb = ctypes.sizeof(DISPLAY_DEVICE)  # pylint: disable=attribute-defined-outside-init

        if not user32.EnumDisplayDevicesW(None, device_index, ctypes.byref(device), 0):
            break

        # Only process active display devices
        if device.StateFlags & 0x00000001:  # DISPLAY_DEVICE_ACTIVE
            devmode = DEVMODE()  # pylint: disable=attribute-defined-outside-init
            devmode.dmSize = ctypes.sizeof(DEVMODE)  # pylint: disable=attribute-defined-outside-init

            if user32.EnumDisplaySettingsW(
                device.DeviceName, ENUM_CURRENT_SETTINGS, ctypes.byref(devmode)
            ):
                # Create a RECT structure for this monitor
                # Note: This method doesn't give us exact positions, so we estimate
                # based on virtual screen metrics
                width = devmode.dmPelsWidth
                height = devmode.dmPelsHeight

                # Get virtual screen position
                virtual_left = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
                virtual_top = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN

                # Estimate position (this is approximate)
                # Primary monitor is typically at (0, 0)
                is_primary = not primary_found
                if is_primary:
                    left = 0
                    top = 0
                    primary_found = True
                else:
                    # For secondary monitors, estimate position
                    # This is a simplified approach
                    left = virtual_left + (len(monitors) * width)
                    top = virtual_top

                # Create a RECT structure
                bounds = RECT()  # pylint: disable=attribute-defined-outside-init
                bounds.left = left  # pylint: disable=attribute-defined-outside-init
                bounds.top = top  # pylint: disable=attribute-defined-outside-init
                bounds.right = left + width  # pylint: disable=attribute-defined-outside-init
                bounds.bottom = top + height  # pylint: disable=attribute-defined-outside-init

                monitor = MonitorInfo(None, bounds, is_primary)
                monitors.append(monitor)

        device_index += 1

    if len(monitors) == 0:
        raise RuntimeError("No monitors detected using alternative method")

    return monitors




def convert_to_virtual_coords(monitor_index, x, y, monitors):
    """
    Convert per-monitor coordinates to virtual screen coordinates.

    Args:
        monitor_index: Index of the monitor (0-based).
        x: X coordinate relative to monitor.
        y: Y coordinate relative to monitor.
        monitors: List of MonitorInfo objects.

    Returns:
        tuple[int, int]: Virtual screen coordinates (x, y).

    Raises:
        ValueError: If monitor_index is invalid or coordinates are out of range.
    """
    if monitor_index < 0:
        raise ValueError(f"Monitor index must be non-negative, got {monitor_index}")

    if monitor_index >= len(monitors):
        raise ValueError(
            f"Monitor index {monitor_index} out of range. "
            f"Available monitors: 0-{len(monitors) - 1}"
        )

    monitor = monitors[monitor_index]

    if x < 0 or x >= monitor.width:
        raise ValueError(
            f"X coordinate {x} out of range for monitor {monitor_index} "
            f"(width: {monitor.width})"
        )

    if y < 0 or y >= monitor.height:
        raise ValueError(
            f"Y coordinate {y} out of range for monitor {monitor_index} "
            f"(height: {monitor.height})"
        )

    virtual_x = monitor.left + x
    virtual_y = monitor.top + y

    return virtual_x, virtual_y


def click_at(x, y):
    """
    Perform a mouse click at the specified virtual screen coordinates.

    Args:
        x: Virtual screen X coordinate.
        y: Virtual screen Y coordinate.

    Raises:
        RuntimeError: If the click operation fails.
    """
    # Move cursor to position
    if not user32.SetCursorPos(int(x), int(y)):
        raise RuntimeError(f"Failed to set cursor position to ({x}, {y})")

    # Create mouse down input
    mouse_down = INPUT()  # pylint: disable=attribute-defined-outside-init
    mouse_down.type = INPUT_MOUSE  # pylint: disable=attribute-defined-outside-init
    mouse_down.mi.dx = 0  # pylint: disable=attribute-defined-outside-init
    mouse_down.mi.dy = 0  # pylint: disable=attribute-defined-outside-init
    mouse_down.mi.mouseData = 0  # pylint: disable=attribute-defined-outside-init
    mouse_down.mi.dwFlags = MOUSEEVENTF_LEFTDOWN  # pylint: disable=attribute-defined-outside-init
    mouse_down.mi.time = 0  # pylint: disable=attribute-defined-outside-init
    mouse_down.mi.dwExtraInfo = None  # pylint: disable=attribute-defined-outside-init

    # Create mouse up input
    mouse_up = INPUT()  # pylint: disable=attribute-defined-outside-init
    mouse_up.type = INPUT_MOUSE  # pylint: disable=attribute-defined-outside-init
    mouse_up.mi.dx = 0  # pylint: disable=attribute-defined-outside-init
    mouse_up.mi.dy = 0  # pylint: disable=attribute-defined-outside-init
    mouse_up.mi.mouseData = 0  # pylint: disable=attribute-defined-outside-init
    mouse_up.mi.dwFlags = MOUSEEVENTF_LEFTUP  # pylint: disable=attribute-defined-outside-init
    mouse_up.mi.time = 0  # pylint: disable=attribute-defined-outside-init
    mouse_up.mi.dwExtraInfo = None  # pylint: disable=attribute-defined-outside-init

    # Send inputs
    if user32.SendInput(1, POINTER(INPUT)(mouse_down), ctypes.sizeof(INPUT)) != 1:
        raise RuntimeError("Failed to send mouse down event")

    if user32.SendInput(1, POINTER(INPUT)(mouse_up), ctypes.sizeof(INPUT)) != 1:
        raise RuntimeError("Failed to send mouse up event")


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
        "loops": 10,
        "wait_between_clicks": 1.0,
        "wait_between_loops": 2.0,
        "coordinates": [],
    }

    for key, default_value in defaults.items():
        if key not in config:
            config[key] = default_value

    return config


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
        return

    if not isinstance(config["coordinates"], list):
        raise ValueError("coordinates must be a list")

    if len(config["coordinates"]) == 0:
        raise ValueError("At least one coordinate must be specified")

    for i, coord in enumerate(config["coordinates"]):
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

    print(f"Starting click loop: {loops} iterations")
    print(f"Coordinates to click: {len(coordinates)}")
    print(f"Wait between clicks: {wait_between_clicks}s")
    print(f"Wait between loops: {wait_between_loops}s")
    print()

    # Convert all coordinates to virtual coordinates upfront
    virtual_coords = []
    for coord in coordinates:
        virtual_x, virtual_y = convert_to_virtual_coords(
            coord["monitor"], coord["x"], coord["y"], monitors
        )
        virtual_coords.append((virtual_x, virtual_y))

    for loop_num in range(1, loops + 1):
        print(f"Loop {loop_num}/{loops}")

        for coord_idx, (virtual_x, virtual_y) in enumerate(virtual_coords):
            coord = coordinates[coord_idx]
            print(
                f"  Clicking monitor {coord['monitor']} "
                f"at ({coord['x']}, {coord['y']}) "
                f"[virtual: ({virtual_x}, {virtual_y})]"
            )

            click_at(virtual_x, virtual_y)

            if coord_idx < len(virtual_coords) - 1:
                time.sleep(wait_between_clicks)

        if loop_num < loops:
            print(f"Waiting {wait_between_loops}s before next loop...")
            time.sleep(wait_between_loops)
            print()

    print("Click loop completed!")


def print_monitor_info(monitors):
    """Print information about detected monitors."""
    print("Detected monitors:")
    for idx, monitor in enumerate(monitors):
        primary_str = " (PRIMARY)" if monitor.is_primary else ""
        print(
            f"  Monitor {idx}: {monitor.width}x{monitor.height} "
            f"at ({monitor.left}, {monitor.top}){primary_str}"
        )
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated mouse clicking script with multi-monitor support"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file (default: config.json)",
    )
    parser.add_argument(
        "--loops",
        type=int,
        help="Number of loop iterations (overrides config)",
    )
    parser.add_argument(
        "--wait-clicks",
        type=float,
        help="Wait time between clicks in seconds (overrides config)",
    )
    parser.add_argument(
        "--wait-loops",
        type=float,
        help="Wait time between loops in seconds (overrides config)",
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Warning: Configuration file '{args.config}' not found. Using defaults.")
        config = {
            "loops": 10,
            "wait_between_clicks": 1.0,
            "wait_between_loops": 2.0,
            "coordinates": [],
        }

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
        print(f"Error: Invalid configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Detect monitors
    try:
        monitors = get_monitors()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if len(monitors) == 0:
        print("Error: No monitors detected", file=sys.stderr)
        sys.exit(1)

    print_monitor_info(monitors)

    # Validate coordinates against monitors
    if len(config["coordinates"]) == 0:
        print("Error: No coordinates specified in configuration", file=sys.stderr)
        sys.exit(1)

    try:
        for coord in config["coordinates"]:
            convert_to_virtual_coords(
                coord["monitor"], coord["x"], coord["y"], monitors
            )
    except ValueError as e:
        print(f"Error: Invalid coordinate: {e}", file=sys.stderr)
        sys.exit(1)

    # Run the click loop
    try:
        run_click_loop(config, monitors)
    except (ValueError, RuntimeError) as e:
        print(f"Error during execution: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
