"""Tests for coordinate conversion functions."""

import pytest

from clickloop.__main__ import convert_to_virtual_coords


class TestConvertToVirtualCoords:
    """Tests for convert_to_virtual_coords function."""

    def test_convert_valid_coordinates_primary_monitor(self, sample_monitors):
        """Test converting coordinates on primary monitor."""
        x, y = convert_to_virtual_coords(0, 100, 200, sample_monitors)
        assert x == 100
        assert y == 200

    def test_convert_valid_coordinates_secondary_monitor(self, sample_monitors):
        """Test converting coordinates on secondary monitor."""
        x, y = convert_to_virtual_coords(1, 300, 400, sample_monitors)
        assert x == 1920 + 300  # monitor.left + x
        assert y == 400  # monitor.top + y

    def test_convert_coordinates_at_origin(self, sample_monitors):
        """Test converting coordinates at monitor origin."""
        x, y = convert_to_virtual_coords(0, 0, 0, sample_monitors)
        assert x == 0
        assert y == 0

    def test_convert_coordinates_at_monitor_edge(self, sample_monitors):
        """Test converting coordinates at monitor edge."""
        # Monitor 0 is 1920x1080, so max coords are 1919, 1079
        x, y = convert_to_virtual_coords(0, 1919, 1079, sample_monitors)
        assert x == 1919
        assert y == 1079

    def test_convert_negative_monitor_index(self, sample_monitors):
        """Test conversion fails with negative monitor index."""
        with pytest.raises(ValueError, match="Monitor index must be non-negative"):
            convert_to_virtual_coords(-1, 100, 200, sample_monitors)

    def test_convert_invalid_monitor_index(self, sample_monitors):
        """Test conversion fails with out-of-range monitor index."""
        with pytest.raises(ValueError, match="Monitor index 2 out of range"):
            convert_to_virtual_coords(2, 100, 200, sample_monitors)

    def test_convert_x_out_of_range_negative(self, sample_monitors):
        """Test conversion fails with negative x coordinate."""
        with pytest.raises(ValueError, match="X coordinate -1 out of range"):
            convert_to_virtual_coords(0, -1, 200, sample_monitors)

    def test_convert_x_out_of_range_too_large(self, sample_monitors):
        """Test conversion fails with x coordinate >= monitor width."""
        with pytest.raises(ValueError, match="X coordinate 1920 out of range"):
            convert_to_virtual_coords(0, 1920, 200, sample_monitors)

    def test_convert_y_out_of_range_negative(self, sample_monitors):
        """Test conversion fails with negative y coordinate."""
        with pytest.raises(ValueError, match="Y coordinate -1 out of range"):
            convert_to_virtual_coords(0, 100, -1, sample_monitors)

    def test_convert_y_out_of_range_too_large(self, sample_monitors):
        """Test conversion fails with y coordinate >= monitor height."""
        with pytest.raises(ValueError, match="Y coordinate 1080 out of range"):
            convert_to_virtual_coords(0, 100, 1080, sample_monitors)

    def test_convert_with_single_monitor(self):
        """Test conversion with single monitor setup."""
        from ctypes.wintypes import RECT
        from clickloop.__main__ import MonitorInfo

        monitor_bounds = RECT()
        monitor_bounds.left = 0
        monitor_bounds.top = 0
        monitor_bounds.right = 1920
        monitor_bounds.bottom = 1080

        monitors = [MonitorInfo(None, monitor_bounds, True)]
        x, y = convert_to_virtual_coords(0, 500, 600, monitors)
        assert x == 500
        assert y == 600
