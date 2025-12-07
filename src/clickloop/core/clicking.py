"""Mouse clicking functionality."""

import ctypes
from ctypes import POINTER, Structure, c_long, c_uint
from ctypes.wintypes import DWORD

# Windows API structures and constants
INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


class MOUSEINPUT(Structure):  # pylint: disable=too-few-public-methods
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
user32 = ctypes.windll.user32


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
