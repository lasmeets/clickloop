"""Tests for clicking functions."""

from unittest.mock import patch

import pytest

from clickloop.__main__ import click_at, run_click_loop


class TestClickAt:
    """Tests for click_at function."""

    @patch("clickloop.__main__.user32")
    def test_click_at_success(self, mock_user32):
        """Test successful click at coordinates."""
        mock_user32.SetCursorPos.return_value = True
        mock_user32.SendInput.return_value = 1

        click_at(100, 200)

        # Verify SetCursorPos was called with correct coordinates
        mock_user32.SetCursorPos.assert_called_once_with(100, 200)

        # Verify SendInput was called twice (mouse down and mouse up)
        assert mock_user32.SendInput.call_count == 2

    @patch("clickloop.__main__.user32")
    def test_click_at_set_cursor_fails(self, mock_user32):
        """Test that RuntimeError is raised when SetCursorPos fails."""
        mock_user32.SetCursorPos.return_value = False

        with pytest.raises(RuntimeError, match="Failed to set cursor position"):
            click_at(100, 200)

    @patch("clickloop.__main__.user32")
    def test_click_at_send_input_down_fails(self, mock_user32):
        """Test that RuntimeError is raised when SendInput for mouse down fails."""
        mock_user32.SetCursorPos.return_value = True
        mock_user32.SendInput.side_effect = [0, 1]  # First call fails, second succeeds

        with pytest.raises(RuntimeError, match="Failed to send mouse down event"):
            click_at(100, 200)

    @patch("clickloop.__main__.user32")
    def test_click_at_send_input_up_fails(self, mock_user32):
        """Test that RuntimeError is raised when SendInput for mouse up fails."""
        mock_user32.SetCursorPos.return_value = True
        mock_user32.SendInput.side_effect = [1, 0]  # First call succeeds, second fails

        with pytest.raises(RuntimeError, match="Failed to send mouse up event"):
            click_at(100, 200)

    @patch("clickloop.__main__.user32")
    def test_click_at_with_float_coordinates(self, mock_user32):
        """Test click_at converts float coordinates to int."""
        mock_user32.SetCursorPos.return_value = True
        mock_user32.SendInput.return_value = 1

        click_at(100.7, 200.9)

        # Verify coordinates were converted to int
        mock_user32.SetCursorPos.assert_called_once_with(100, 200)


class TestRunClickLoop:
    """Tests for run_click_loop function."""

    @patch("clickloop.__main__.time.sleep")
    @patch("clickloop.__main__.click_at")
    def test_run_click_loop_single_coordinate(self, mock_click_at, mock_sleep, sample_config_minimal, sample_monitors):
        """Test running click loop with single coordinate."""
        config = sample_config_minimal.copy()
        config["loops"] = 2
        config["wait_between_clicks"] = 0.1
        config["wait_between_loops"] = 0.2

        run_click_loop(config, sample_monitors)

        # Should click 2 times (2 loops)
        assert mock_click_at.call_count == 2
        # Should sleep between loops once
        assert mock_sleep.call_count == 1

    @patch("clickloop.__main__.time.sleep")
    @patch("clickloop.__main__.click_at")
    def test_run_click_loop_multiple_coordinates(self, mock_click_at, mock_sleep, sample_config, sample_monitors):
        """Test running click loop with multiple coordinates."""
        config = sample_config.copy()
        config["loops"] = 2

        run_click_loop(config, sample_monitors)

        # Should click 4 times (2 coordinates * 2 loops)
        assert mock_click_at.call_count == 4
        # Should sleep: 1 between clicks per loop (2 loops * 1 sleep) + 1 between loops = 3
        assert mock_sleep.call_count == 3

    @patch("clickloop.__main__.time.sleep")
    @patch("clickloop.__main__.click_at")
    def test_run_click_loop_no_wait_between_clicks(self, mock_click_at, mock_sleep, sample_config, sample_monitors):
        """Test running click loop with zero wait between clicks."""
        config = sample_config.copy()
        config["wait_between_clicks"] = 0
        config["loops"] = 1

        run_click_loop(config, sample_monitors)

        # Should click 2 times (2 coordinates * 1 loop)
        assert mock_click_at.call_count == 2
        # Should not sleep between clicks, only between loops (but only 1 loop, so 0 sleeps)
        assert mock_sleep.call_count == 0

    @patch("clickloop.__main__.time.sleep")
    @patch("clickloop.__main__.click_at")
    def test_run_click_loop_single_loop(self, mock_click_at, mock_sleep, sample_config, sample_monitors):
        """Test running click loop with single loop (no wait between loops)."""
        config = sample_config.copy()
        config["loops"] = 1

        run_click_loop(config, sample_monitors)

        # Should click 2 times (2 coordinates * 1 loop)
        assert mock_click_at.call_count == 2
        # Should sleep between clicks once (2 coordinates - 1)
        assert mock_sleep.call_count == 1

    @patch("clickloop.__main__.time.sleep")
    @patch("clickloop.__main__.click_at")
    @patch("clickloop.__main__.convert_to_virtual_coords")
    def test_run_click_loop_coordinate_conversion(self, mock_convert, mock_click_at, mock_sleep, sample_config, sample_monitors):
        """Test that coordinates are converted to virtual coordinates."""
        config = sample_config.copy()
        config["loops"] = 1

        # Mock coordinate conversion
        mock_convert.side_effect = [(100, 200), (2220, 400)]  # Virtual coords for 2 monitors

        run_click_loop(config, sample_monitors)

        # Verify convert_to_virtual_coords was called for each coordinate
        assert mock_convert.call_count == 2
        # Verify click_at was called with virtual coordinates
        mock_click_at.assert_any_call(100, 200)
        mock_click_at.assert_any_call(2220, 400)

    @patch("clickloop.__main__.time.sleep")
    @patch("clickloop.__main__.click_at")
    def test_run_click_loop_handles_click_error(self, mock_click_at, mock_sleep, sample_config, sample_monitors):
        """Test that RuntimeError from click_at is propagated."""
        config = sample_config.copy()
        config["loops"] = 1

        mock_click_at.side_effect = RuntimeError("Click failed")

        with pytest.raises(RuntimeError, match="Click failed"):
            run_click_loop(config, sample_monitors)
