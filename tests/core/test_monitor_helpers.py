"""Tests for monitor helper functions."""

from unittest.mock import patch
from ctypes.wintypes import RECT

from clickloop.core.monitors import get_monitor_for_point, print_monitor_info


class TestGetMonitorForPoint:
    """Tests for get_monitor_for_point function."""

    def test_find_monitor_primary(self, sample_monitors):
        """Test finding monitor for point on primary monitor."""
        monitor_idx, monitor = get_monitor_for_point(100, 200, sample_monitors)

        assert monitor_idx == 0
        assert monitor is sample_monitors[0]
        assert monitor.is_primary is True

    def test_find_monitor_secondary(self, sample_monitors):
        """Test finding monitor for point on secondary monitor."""
        # Point on secondary monitor (starts at x=1920)
        monitor_idx, monitor = get_monitor_for_point(2000, 500, sample_monitors)

        assert monitor_idx == 1
        assert monitor is sample_monitors[1]
        assert monitor.is_primary is False

    def test_find_monitor_at_left_edge(self, sample_monitors):
        """Test finding monitor for point at left edge."""
        monitor_idx, monitor = get_monitor_for_point(0, 100, sample_monitors)

        assert monitor_idx == 0
        assert monitor is sample_monitors[0]

    def test_find_monitor_at_right_edge(self, sample_monitors):
        """Test finding monitor for point at right edge (exclusive)."""
        # Right edge is exclusive, so 1920 should be on monitor 1
        monitor_idx, monitor = get_monitor_for_point(1920, 100, sample_monitors)

        assert monitor_idx == 1
        assert monitor is sample_monitors[1]

    def test_find_monitor_at_top_edge(self, sample_monitors):
        """Test finding monitor for point at top edge."""
        monitor_idx, monitor = get_monitor_for_point(100, 0, sample_monitors)

        assert monitor_idx == 0
        assert monitor is sample_monitors[0]

    def test_find_monitor_at_bottom_edge(self, sample_monitors):
        """Test finding monitor for point at bottom edge (exclusive)."""
        # Bottom edge is exclusive, so 1080 should be outside
        monitor_idx, monitor = get_monitor_for_point(100, 1080, sample_monitors)

        assert monitor_idx == -1
        assert monitor is None

    def test_point_outside_all_monitors_left(self, sample_monitors):
        """Test point outside all monitors (to the left)."""
        monitor_idx, monitor = get_monitor_for_point(-100, 500, sample_monitors)

        assert monitor_idx == -1
        assert monitor is None

    def test_point_outside_all_monitors_right(self, sample_monitors):
        """Test point outside all monitors (to the right)."""
        monitor_idx, monitor = get_monitor_for_point(5000, 500, sample_monitors)

        assert monitor_idx == -1
        assert monitor is None

    def test_point_outside_all_monitors_top(self, sample_monitors):
        """Test point outside all monitors (above)."""
        monitor_idx, monitor = get_monitor_for_point(100, -100, sample_monitors)

        assert monitor_idx == -1
        assert monitor is None

    def test_point_outside_all_monitors_bottom(self, sample_monitors):
        """Test point outside all monitors (below)."""
        monitor_idx, monitor = get_monitor_for_point(100, 2000, sample_monitors)

        assert monitor_idx == -1
        assert monitor is None

    def test_point_at_monitor_corner(self, sample_monitors):
        """Test point at monitor corner."""
        # Top-left corner of primary monitor
        monitor_idx, monitor = get_monitor_for_point(0, 0, sample_monitors)

        assert monitor_idx == 0
        assert monitor is sample_monitors[0]

    def test_point_at_monitor_boundary_between_monitors(self, sample_monitors):
        """Test point at boundary between two monitors."""
        # At x=1920, which is the boundary
        # Left monitor: 0 <= x < 1920
        # Right monitor: 1920 <= x < 3840
        # So 1920 belongs to the right monitor
        monitor_idx, monitor = get_monitor_for_point(1920, 500, sample_monitors)

        assert monitor_idx == 1
        assert monitor is sample_monitors[1]

    def test_with_single_monitor(self):
        """Test with single monitor setup."""
        monitor_bounds = RECT()
        monitor_bounds.left = 0
        monitor_bounds.top = 0
        monitor_bounds.right = 1920
        monitor_bounds.bottom = 1080

        from clickloop.core.monitors import MonitorInfo
        monitors = [MonitorInfo(None, monitor_bounds, True)]

        monitor_idx, monitor = get_monitor_for_point(500, 600, monitors)

        assert monitor_idx == 0
        assert monitor is monitors[0]

    def test_with_empty_monitor_list(self):
        """Test with empty monitor list."""
        monitor_idx, monitor = get_monitor_for_point(100, 200, [])

        assert monitor_idx == -1
        assert monitor is None


class TestPrintMonitorInfo:
    """Tests for print_monitor_info function."""

    @patch("clickloop.core.monitors.logger")
    def test_print_monitor_info_single_monitor(self, mock_logger, sample_monitors):
        """Test printing info for single monitor."""
        single_monitor = [sample_monitors[0]]
        print_monitor_info(single_monitor)

        # Verify logger.info was called
        assert mock_logger.info.call_count == 2  # Header + monitor info

        # Check that monitor info was logged - check call arguments
        # First call is "Detected monitors:", second is monitor info
        monitor_call = mock_logger.info.call_args_list[1]
        assert monitor_call[0][0] == "  Monitor %s: %sx%s at (%s, %s)%s"
        assert monitor_call[0][1] == 0  # Monitor index

    @patch("clickloop.core.monitors.logger")
    def test_print_monitor_info_multiple_monitors(self, mock_logger, sample_monitors):
        """Test printing info for multiple monitors."""
        print_monitor_info(sample_monitors)

        # Verify logger.info was called (header + 2 monitors)
        assert mock_logger.info.call_count == 3

        # Check that both monitors were logged - check call arguments
        # First call is "Detected monitors:", then monitor 0, then monitor 1
        monitor_0_call = mock_logger.info.call_args_list[1]
        monitor_1_call = mock_logger.info.call_args_list[2]
        assert monitor_0_call[0][1] == 0  # Monitor 0 index
        assert monitor_1_call[0][1] == 1  # Monitor 1 index

    @patch("clickloop.core.monitors.logger")
    def test_print_monitor_info_shows_primary(self, mock_logger, sample_monitors):
        """Test that primary monitor is marked correctly."""
        print_monitor_info(sample_monitors)

        # Check that PRIMARY is shown for monitor 0
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        primary_calls = [call for call in log_calls if "PRIMARY" in call]
        assert len(primary_calls) == 1

    @patch("clickloop.core.monitors.logger")
    def test_print_monitor_info_format(self, mock_logger, sample_monitors):
        """Test that monitor info is formatted correctly."""
        print_monitor_info(sample_monitors)

        # Get the monitor info call (second call, first is header)
        monitor_call = mock_logger.info.call_args_list[1]

        # Verify format includes width, height, position
        call_str = str(monitor_call)
        assert "1920" in call_str  # width
        assert "1080" in call_str  # height
        assert "0" in call_str  # left position
        assert "0" in call_str  # top position
