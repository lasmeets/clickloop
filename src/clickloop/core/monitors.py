"""Monitor detection and utilities."""

import ctypes
import logging
from ctypes import POINTER, Structure, WINFUNCTYPE, c_long, windll
from ctypes.wintypes import BOOL, DWORD, HMONITOR, HDC, LPARAM, RECT

logger = logging.getLogger("clickloop")


# Windows API structures and constants
class MONITORINFO(Structure):  # pylint: disable=too-few-public-methods
    """Information about a display monitor."""

    _fields_ = [
        ("cbSize", DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", DWORD),
    ]


MONITORINFOF_PRIMARY = 1


class DisplayDevice(Structure):  # pylint: disable=invalid-name,too-few-public-methods
    """Display device information."""

    _fields_ = [
        ("cb", DWORD),
        ("DeviceName", ctypes.c_wchar * 32),
        ("DeviceString", ctypes.c_wchar * 128),
        ("StateFlags", DWORD),
        ("DeviceID", ctypes.c_wchar * 128),
        ("DeviceKey", ctypes.c_wchar * 128),
    ]


class DevMode(Structure):  # pylint: disable=invalid-name,too-few-public-methods
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


ENUM_CURRENT_SETTINGS = -1  # pylint: disable=invalid-name


# Windows API function prototypes
user32 = windll.user32

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
        info.cbSize = DWORD(ctypes.sizeof(MONITORINFO))  # pylint: disable=attribute-defined-outside-init,invalid-name
        if not user32.GetMonitorInfoW(hmonitor, ctypes.byref(info)):
            error_code = ctypes.get_last_error()
            if error_code != 0:
                logger.warning("GetMonitorInfoW failed with error %s", error_code)
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
    # Set up function prototypes
    user32.EnumDisplayDevicesW.argtypes = [
        ctypes.c_wchar_p, DWORD, POINTER(DisplayDevice), DWORD
    ]
    user32.EnumDisplayDevicesW.restype = BOOL

    user32.EnumDisplaySettingsW.argtypes = [
        ctypes.c_wchar_p, DWORD, POINTER(DevMode)
    ]
    user32.EnumDisplaySettingsW.restype = BOOL

    monitors = []
    device_index = 0
    primary_found = False

    while True:
        device = DisplayDevice()  # pylint: disable=attribute-defined-outside-init
        device.cb = ctypes.sizeof(DisplayDevice)  # pylint: disable=attribute-defined-outside-init,invalid-name

        if not user32.EnumDisplayDevicesW(None, device_index, ctypes.byref(device), 0):
            break

        # Only process active display devices
        if device.StateFlags & 0x00000001:  # DISPLAY_DEVICE_ACTIVE
            devmode = DevMode()  # pylint: disable=attribute-defined-outside-init
            devmode.dmSize = ctypes.sizeof(DevMode)  # pylint: disable=attribute-defined-outside-init,invalid-name

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


def get_monitor_for_point(x, y, monitors):
    """
    Find which monitor contains the given virtual screen coordinates.

    Args:
        x: Virtual screen X coordinate.
        y: Virtual screen Y coordinate.
        monitors: List of MonitorInfo objects.

    Returns:
        tuple[int, MonitorInfo]: Monitor index and MonitorInfo object, or (-1, None) if not found.
    """
    for idx, monitor in enumerate(monitors):
        if (monitor.left <= x < monitor.right and
                monitor.top <= y < monitor.bottom):
            return idx, monitor

    return -1, None


def print_monitor_info(monitors):
    """Print information about detected monitors."""
    logger.info("Detected monitors:")
    for idx, monitor in enumerate(monitors):
        primary_str = " (PRIMARY)" if monitor.is_primary else ""
        logger.info(
            "  Monitor %s: %sx%s at (%s, %s)%s",
            idx, monitor.width, monitor.height, monitor.left, monitor.top, primary_str
        )

