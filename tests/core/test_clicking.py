"""Tests for clicking functions."""

from unittest.mock import patch

import pytest

from clickloop.commands.run import run_click_loop
from clickloop.core.clicking import click_at


class TestClickAt:
    """Tests for click_at function."""

    @patch("clickloop.core.clicking.user32")
    def test_click_at_success(self, mock_user32):
        """Test successful click at coordinates."""
        mock_user32.SetCursorPos.return_value = True
        mock_user32.SendInput.return_value = 1

        click_at(100, 200)

        # Verify SetCursorPos was called with correct coordinates
        mock_user32.SetCursorPos.assert_called_once_with(100, 200)

        # Verify SendInput was called twice (mouse down and mouse up)
        assert mock_user32.SendInput.call_count == 2

    @patch("clickloop.core.clicking.user32")
    def test_click_at_set_cursor_fails_immediately(self, mock_user32):
        """Test that RuntimeError is raised after retries when SetCursorPos fails."""
        mock_user32.SetCursorPos.return_value = False

        with pytest.raises(RuntimeError, match="Failed to set cursor position"):
            click_at(100, 200, max_retries=1)

    @patch("clickloop.core.clicking.time.sleep")
    @patch("clickloop.core.clicking.user32")
    def test_click_at_retries_on_set_cursor_failure(self, mock_user32, mock_sleep):
        """Test that click_at retries when SetCursorPos fails initially."""
        # Fail twice, succeed on third
        mock_user32.SetCursorPos.side_effect = [False, False, True]
        mock_user32.SendInput.return_value = 1

        click_at(100, 200, max_retries=3)

        # SetCursorPos should be called 3 times (once per attempt)
        assert mock_user32.SetCursorPos.call_count == 3
        # Should have slept twice (between retries)
        assert mock_sleep.call_count == 2

    @patch("clickloop.core.clicking.time.sleep")
    @patch("clickloop.core.clicking.user32")
    def test_click_at_exponential_backoff(self, mock_user32, mock_sleep):
        """Test that click_at uses exponential backoff between retries."""
        # Fail all attempts
        mock_user32.SetCursorPos.return_value = False

        with pytest.raises(RuntimeError):
            click_at(100, 200, max_retries=3)

        # Should sleep with exponential backoff: 0.5s, 1.0s
        mock_sleep.assert_any_call(0.5)
        mock_sleep.assert_any_call(1.0)
        assert mock_sleep.call_count == 2

    @patch("clickloop.core.clicking.user32")
    def test_click_at_send_input_down_fails_then_succeeds(self, mock_user32):
        """Test that click_at retries when SendInput for mouse down fails."""
        mock_user32.SetCursorPos.return_value = True
        # First attempt: SetCursorPos succeeds but SendInput fails
        # Second attempt: all succeed
        mock_user32.SendInput.side_effect = [0, 1, 1]  # First click fails on down event, second succeeds

        with patch("clickloop.core.clicking.time.sleep"):
            click_at(100, 200, max_retries=2)

        # SetCursorPos should be called twice (once per attempt)
        assert mock_user32.SetCursorPos.call_count == 2
        # SendInput should be called 3 times total (first attempt fails early, second succeeds with 2 calls)
        assert mock_user32.SendInput.call_count == 3

    @patch("clickloop.core.clicking.user32")
    def test_click_at_with_float_coordinates(self, mock_user32):
        """Test click_at converts float coordinates to int."""
        mock_user32.SetCursorPos.return_value = True
        mock_user32.SendInput.return_value = 1

        click_at(100.7, 200.9)

        # Verify coordinates were converted to int
        mock_user32.SetCursorPos.assert_called_once_with(100, 200)

    @patch("clickloop.core.clicking.user32")
    def test_click_at_default_max_retries_is_three(self, mock_user32):
        """Test that default max_retries is 3."""
        mock_user32.SetCursorPos.return_value = False

        with pytest.raises(RuntimeError):
            click_at(100, 200)  # No max_retries argument

        # Should attempt 3 times by default
        assert mock_user32.SetCursorPos.call_count == 3


class TestRunClickLoop:
    """Tests for run_click_loop function."""

    @patch("clickloop.commands.run.time.sleep")
    @patch("clickloop.commands.run.click_at")
    def test_run_click_loop_single_coordinate(
        self, mock_click_at, mock_sleep, sample_config_minimal, sample_monitors
    ):
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

    @patch("clickloop.commands.run.time.sleep")
    @patch("clickloop.commands.run.click_at")
    def test_run_click_loop_multiple_coordinates(
        self, mock_click_at, mock_sleep, sample_config, sample_monitors
    ):
        """Test running click loop with multiple coordinates."""
        config = sample_config.copy()
        config["loops"] = 2

        run_click_loop(config, sample_monitors)

        # Should click 4 times (2 coordinates * 2 loops)
        assert mock_click_at.call_count == 4
        # Should sleep: 1 between clicks per loop (2 loops * 1 sleep) + 1 between loops = 3
        assert mock_sleep.call_count == 3

    @patch("clickloop.commands.run.time.sleep")
    @patch("clickloop.commands.run.click_at")
    def test_run_click_loop_no_wait_between_clicks(
        self, mock_click_at, mock_sleep, sample_config, sample_monitors
    ):
        """Test running click loop with zero wait between clicks."""
        config = sample_config.copy()
        config["wait_between_clicks"] = 0
        config["loops"] = 1

        run_click_loop(config, sample_monitors)

        # Should click 2 times (2 coordinates * 1 loop)
        assert mock_click_at.call_count == 2
        # Should not sleep between clicks, only between loops (but only 1 loop, so 0 sleeps)
        assert mock_sleep.call_count == 0

    @patch("clickloop.commands.run.time.sleep")
    @patch("clickloop.commands.run.click_at")
    def test_run_click_loop_single_loop(
        self, mock_click_at, mock_sleep, sample_config, sample_monitors
    ):
        """Test running click loop with single loop (no wait between loops)."""
        config = sample_config.copy()
        config["loops"] = 1

        run_click_loop(config, sample_monitors)

        # Should click 2 times (2 coordinates * 1 loop)
        assert mock_click_at.call_count == 2
        # Should sleep between clicks once (2 coordinates - 1)
        assert mock_sleep.call_count == 1

    @patch("clickloop.commands.run.click_at")
    @patch("clickloop.commands.run.convert_to_virtual_coords")
    def test_run_click_loop_coordinate_conversion(
        self, mock_convert, mock_click_at, sample_config, sample_monitors
    ):
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

    @patch("clickloop.commands.run.time.sleep")
    @patch("clickloop.commands.run.click_at")
    def test_run_click_loop_handles_click_error(
        self, mock_click_at, _mock_sleep, sample_config, sample_monitors
    ):
        """Test that RuntimeError from click_at is caught and logged, loop continues."""
        config = sample_config.copy()
        config["loops"] = 2
        config["coordinates"] = [
            {"monitor": 0, "x": 100, "y": 200},
            {"monitor": 1, "x": 300, "y": 400},
        ]

        # First click in first loop fails, rest succeed
        mock_click_at.side_effect = [
            RuntimeError("Click failed"),  # Loop 1, coord 0
            None,                           # Loop 1, coord 1
            None,                           # Loop 2, coord 0
            None,                           # Loop 2, coord 1
        ]

        # Should not raise - errors are caught and logged
        run_click_loop(config, sample_monitors)

        # All 4 clicks should still be attempted
        assert mock_click_at.call_count == 4

    @patch("clickloop.commands.run.time.sleep")
    @patch("clickloop.commands.run.click_at")
    def test_run_click_loop_skips_failed_clicks(
        self, mock_click_at, _mock_sleep, sample_config, sample_monitors
    ):
        """Test that failed clicks are skipped but loop continues."""
        config = sample_config.copy()
        config["loops"] = 1
        config["coordinates"] = [
            {"monitor": 0, "x": 100, "y": 200},
        ]

        # All clicks fail
        mock_click_at.side_effect = RuntimeError("All clicks fail")

        # Should not raise - error is logged and skipped
        run_click_loop(config, sample_monitors)

        # Click should still be attempted
        assert mock_click_at.call_count == 1
