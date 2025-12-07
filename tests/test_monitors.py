"""Tests for monitor detection functions."""

import ctypes
from unittest.mock import patch

import pytest

from clickloop.__main__ import get_monitors
from clickloop.__main__ import get_monitors_alternative

# Save reference to real byref before it might get patched
_real_byref = ctypes.byref



class TestGetMonitors:
    """Tests for get_monitors function."""

    @patch("clickloop.__main__.user32")
    @patch("clickloop.__main__.MonitorEnumProc")
    def test_get_monitors_success(self, mock_enum_proc_class, mock_user32):
        """Test successful monitor enumeration."""
        # Setup mock monitor info structures

    @patch("clickloop.__main__.user32")
    def test_get_monitors_enumeration_fails(self, mock_user32):
        """Test that RuntimeError is raised when enumeration fails."""
        mock_user32.EnumDisplayMonitors.return_value = False

        with pytest.raises(RuntimeError, match="Failed to enumerate display monitors"):
            get_monitors()

    @patch("clickloop.__main__.user32")
    def test_get_monitors_no_monitors_detected(self, mock_user32):
        """Test that RuntimeError is raised when no monitors are detected."""
        # Mock EnumDisplayMonitors to return True but callback never called
        mock_user32.EnumDisplayMonitors.return_value = True




class TestGetMonitorsAlternative:
    """Tests for get_monitors_alternative function."""

    @patch("clickloop.__main__.user32")
    @patch("clickloop.__main__.ctypes.byref")
    def test_get_monitors_alternative_success(self, mock_byref, mock_user32):
        """Test successful alternative monitor detection."""
        # Track device structures created in the function
        # We identify them by their attributes since the classes are defined inside the function
        device_structures = []
        devmode_structures = []

        def byref_side_effect(obj):
            # Store references to the actual structures so we can modify them
            # Check for attributes to identify structure types
            if hasattr(obj, 'StateFlags') and hasattr(obj, 'DeviceName'):
                device_structures.append(obj)
            elif hasattr(obj, 'dmPelsWidth') and hasattr(obj, 'dmPelsHeight'):
                devmode_structures.append(obj)
            # Use the real byref (not the mocked one) to avoid recursion
            return _real_byref(obj)

        mock_byref.side_effect = byref_side_effect

        # Mock EnumDisplayDevicesW to return two monitors and modify structures
        device_calls = [0]

        def enum_display_devices_side_effect(_device_name, _device_index, _device_ptr, _flags):
            device_calls[0] += 1
            if device_calls[0] == 1:
                # Modify the actual structure that was passed
                if device_structures:
                    device_structures[0].StateFlags = 0x00000001  # DISPLAY_DEVICE_ACTIVE
                    device_structures[0].DeviceName = "DISPLAY1"
                return True
            if device_calls[0] == 2:
                if len(device_structures) > 1:
                    device_structures[1].StateFlags = 0x00000001  # DISPLAY_DEVICE_ACTIVE
                    device_structures[1].DeviceName = "DISPLAY2"
                return True
            return False

        mock_user32.EnumDisplayDevicesW.side_effect = enum_display_devices_side_effect

        # Mock EnumDisplaySettingsW
        settings_calls = [0]

        def enum_display_settings_side_effect(_device_name, _mode_num, _devmode_ptr):
            settings_calls[0] += 1
            if settings_calls[0] == 1 and devmode_structures:
                devmode_structures[0].dmPelsWidth = 1920
                devmode_structures[0].dmPelsHeight = 1080
            if settings_calls[0] == 2 and len(devmode_structures) > 1:
                devmode_structures[1].dmPelsWidth = 1920
                devmode_structures[1].dmPelsHeight = 1080
            return True

        mock_user32.EnumDisplaySettingsW.side_effect = enum_display_settings_side_effect

        # Mock GetSystemMetrics
        def get_system_metrics_side_effect(metric):
            if metric == 76:  # SM_XVIRTUALSCREEN
                return 0
            if metric == 77:  # SM_YVIRTUALSCREEN
                return 0
            return 0

        mock_user32.GetSystemMetrics.side_effect = get_system_metrics_side_effect

        monitors = get_monitors_alternative()

        assert len(monitors) == 2
        assert monitors[0].is_primary is True
        assert monitors[0].width == 1920
        assert monitors[0].height == 1080
        assert monitors[1].is_primary is False

    @patch("clickloop.__main__.user32")
    def test_get_monitors_alternative_no_monitors(self, mock_user32):
        """Test that RuntimeError is raised when no monitors detected."""
        mock_user32.EnumDisplayDevicesW.return_value = False

        with pytest.raises(RuntimeError, match="No monitors detected using alternative method"):
            get_monitors_alternative()
