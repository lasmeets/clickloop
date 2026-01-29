"""Tests for run command - click loop execution."""

from unittest.mock import Mock, patch

import pytest

from clickloop.commands.run import run_command


class TestRunCommand:
    """Tests for run_command function."""

    @patch("clickloop.commands.run.run_click_loop")
    @patch("clickloop.commands.run.print_monitor_info")
    @patch("clickloop.commands.run.get_monitors")
    @patch("clickloop.commands.run.convert_to_virtual_coords")
    @patch("clickloop.commands.run.validate_config")
    @patch("clickloop.commands.run.load_config")
    def test_run_command_success(
        self,
        mock_load_config,
        mock_validate_config,
        mock_convert_coords,
        mock_get_monitors,
        mock_print_monitor_info,
        mock_run_click_loop,
        sample_config,
        sample_monitors,
    ):
        """Test successful execution of run command."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        mock_load_config.return_value = sample_config
        mock_get_monitors.return_value = sample_monitors

        run_command(args)

        mock_load_config.assert_called_once_with("test_config.json")
        mock_validate_config.assert_called_once()
        mock_get_monitors.assert_called_once()
        mock_run_click_loop.assert_called_once()

    @patch("clickloop.commands.run.load_config")
    def test_run_command_missing_config_file(self, mock_load_config):
        """Test run command with missing config file raises FileNotFoundError."""
        args = Mock()
        args.config = "nonexistent.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        mock_load_config.side_effect = FileNotFoundError("File not found")

        with pytest.raises(FileNotFoundError):
            run_command(args)

    @patch("clickloop.commands.run.load_config")
    def test_run_command_invalid_config(self, mock_load_config):
        """Test run command with invalid configuration raises ValueError."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        # Provide a config that will fail validation but has coordinates key to avoid KeyError
        mock_load_config.return_value = {"invalid": "config", "coordinates": []}

        with patch("clickloop.commands.run.validate_config") as mock_validate:
            mock_validate.side_effect = ValueError("Invalid config")

            with pytest.raises(ValueError):
                run_command(args)

    @patch("clickloop.commands.run.load_config")
    def test_run_command_no_monitors(self, mock_load_config, sample_config):
        """Test run command when no monitors detected raises RuntimeError."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        mock_load_config.return_value = sample_config

        with patch("clickloop.commands.run.validate_config"), \
             patch("clickloop.commands.run.get_monitors") as mock_get_monitors:
            mock_get_monitors.return_value = []

            with pytest.raises(RuntimeError, match="No monitors detected"):
                run_command(args)

    @patch("clickloop.commands.run.load_config")
    def test_run_command_monitor_detection_fails(
        self, mock_load_config, sample_config
    ):
        """Test run command when monitor detection fails raises RuntimeError."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        mock_load_config.return_value = sample_config

        with patch("clickloop.commands.run.validate_config"), \
             patch("clickloop.commands.run.get_monitors") as mock_get_monitors:
            mock_get_monitors.side_effect = RuntimeError("Monitor detection failed")

            with pytest.raises(RuntimeError, match="Monitor detection failed"):
                run_command(args)

    @patch("clickloop.commands.run.load_config")
    def test_run_command_no_coordinates(self, mock_load_config, sample_monitors):
        """Test run command when no coordinates specified raises ValueError."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        config_without_coords = {"loops": 5, "wait_between_clicks": 1.0, "wait_between_loops": 2.0, "coordinates": []}
        mock_load_config.return_value = config_without_coords

        with patch("clickloop.commands.run.validate_config"), \
             patch("clickloop.commands.run.get_monitors") as mock_get_monitors:
            mock_get_monitors.return_value = sample_monitors

            with pytest.raises(ValueError, match="No coordinates specified"):
                run_command(args)

    @patch("clickloop.commands.run.load_config")
    def test_run_command_invalid_coordinate(
        self, mock_load_config, sample_config, sample_monitors
    ):
        """Test run command with invalid coordinate raises ValueError."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        mock_load_config.return_value = sample_config

        with patch("clickloop.commands.run.validate_config"), \
             patch("clickloop.commands.run.get_monitors") as mock_get_monitors, \
             patch("clickloop.commands.run.convert_to_virtual_coords") as mock_convert, \
             patch("clickloop.commands.run.print_monitor_info"):
            mock_get_monitors.return_value = sample_monitors
            mock_convert.side_effect = ValueError("Invalid coordinate")

            with pytest.raises(ValueError, match="Invalid coordinate"):
                run_command(args)

    @patch("clickloop.commands.run.load_config")
    @patch("clickloop.commands.run.run_click_loop")
    @patch("clickloop.commands.run.get_monitors")
    @patch("clickloop.commands.run.validate_config")
    @patch("clickloop.commands.run.convert_to_virtual_coords")
    def test_run_command_cli_override_loops(
        self,
        mock_convert_coords,
        mock_validate_config,
        mock_get_monitors,
        mock_run_click_loop,
        mock_load_config,
        sample_config,
        sample_monitors,
    ):
        """Test that --loops CLI argument overrides config."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = 20
        args.wait_clicks = None
        args.wait_loops = None

        mock_load_config.return_value = sample_config.copy()
        mock_get_monitors.return_value = sample_monitors
        mock_convert_coords.return_value = (100, 200)

        with patch("clickloop.commands.run.print_monitor_info"):
            run_command(args)

            # Verify run_click_loop was called with overridden loops
            call_args = mock_run_click_loop.call_args[0][0]
            assert call_args["loops"] == 20
            assert call_args["wait_between_clicks"] == sample_config["wait_between_clicks"]

    @patch("clickloop.commands.run.load_config")
    @patch("clickloop.commands.run.run_click_loop")
    @patch("clickloop.commands.run.get_monitors")
    @patch("clickloop.commands.run.validate_config")
    @patch("clickloop.commands.run.convert_to_virtual_coords")
    def test_run_command_cli_override_wait_clicks(
        self,
        mock_convert_coords,
        mock_validate_config,
        mock_get_monitors,
        mock_run_click_loop,
        mock_load_config,
        sample_config,
        sample_monitors,
    ):
        """Test that --wait-clicks CLI argument overrides config."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = 2.5
        args.wait_loops = None

        mock_load_config.return_value = sample_config.copy()
        mock_get_monitors.return_value = sample_monitors
        mock_convert_coords.return_value = (100, 200)

        with patch("clickloop.commands.run.print_monitor_info"):
            run_command(args)

            call_args = mock_run_click_loop.call_args[0][0]
            assert call_args["wait_between_clicks"] == 2.5
            assert call_args["loops"] == sample_config["loops"]

    @patch("clickloop.commands.run.load_config")
    @patch("clickloop.commands.run.run_click_loop")
    @patch("clickloop.commands.run.get_monitors")
    @patch("clickloop.commands.run.validate_config")
    @patch("clickloop.commands.run.convert_to_virtual_coords")
    def test_run_command_cli_override_wait_loops(
        self,
        mock_convert_coords,
        mock_validate_config,
        mock_get_monitors,
        mock_run_click_loop,
        mock_load_config,
        sample_config,
        sample_monitors,
    ):
        """Test that --wait-loops CLI argument overrides config."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = 5.0

        mock_load_config.return_value = sample_config.copy()
        mock_get_monitors.return_value = sample_monitors
        mock_convert_coords.return_value = (100, 200)

        with patch("clickloop.commands.run.print_monitor_info"):
            run_command(args)

            call_args = mock_run_click_loop.call_args[0][0]
            assert call_args["wait_between_loops"] == 5.0
            assert call_args["loops"] == sample_config["loops"]

    @patch("clickloop.commands.run.load_config")
    def test_run_command_click_loop_error(
        self, mock_load_config, sample_config, sample_monitors
    ):
        """Test run command when click loop raises an error."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        mock_load_config.return_value = sample_config

        with patch("clickloop.commands.run.validate_config"), \
             patch("clickloop.commands.run.get_monitors") as mock_get_monitors, \
             patch("clickloop.commands.run.convert_to_virtual_coords") as mock_convert, \
             patch("clickloop.commands.run.print_monitor_info"), \
             patch("clickloop.commands.run.run_click_loop") as mock_run:
            mock_get_monitors.return_value = sample_monitors
            mock_convert.return_value = (100, 200)
            mock_run.side_effect = RuntimeError("Click failed")

            with pytest.raises(RuntimeError, match="Click failed"):
                run_command(args)

