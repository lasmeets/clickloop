"""Tests for run command - click loop execution."""

from unittest.mock import Mock, patch

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
    @patch("clickloop.commands.run.logger")
    @patch("clickloop.commands.run.sys")
    def test_run_command_missing_config_file(self, mock_sys, mock_logger, mock_load_config):
        """Test run command with missing config file (uses defaults)."""
        args = Mock()
        args.config = "nonexistent.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        mock_load_config.side_effect = FileNotFoundError()

        with patch("clickloop.commands.run.get_monitors") as mock_get_monitors, \
             patch("clickloop.commands.run.validate_config") as mock_validate:
            mock_get_monitors.return_value = [Mock()]
            # validate_config will fail because default config has no coordinates
            mock_validate.side_effect = ValueError("No coordinates")

            run_command(args)

            mock_logger.warning.assert_called_once()
            # sys.exit may be called multiple times due to multiple error paths
            assert mock_sys.exit.called
            assert mock_sys.exit.call_args[0][0] == 1

    @patch("clickloop.commands.run.load_config")
    @patch("clickloop.commands.run.logger")
    @patch("clickloop.commands.run.sys")
    def test_run_command_invalid_config(self, mock_sys, mock_logger, mock_load_config):
        """Test run command with invalid configuration."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        # Provide a config that will fail validation but has coordinates key to avoid KeyError
        mock_load_config.return_value = {"invalid": "config", "coordinates": []}

        with patch("clickloop.commands.run.validate_config") as mock_validate:
            mock_validate.side_effect = ValueError("Invalid config")

            run_command(args)

            mock_logger.error.assert_called_once()
            assert mock_sys.exit.called
            assert mock_sys.exit.call_args[0][0] == 1

    @patch("clickloop.commands.run.load_config")
    @patch("clickloop.commands.run.logger")
    @patch("clickloop.commands.run.sys")
    def test_run_command_no_monitors(self, mock_sys, mock_logger, mock_load_config, sample_config):
        """Test run command when no monitors detected."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        mock_load_config.return_value = sample_config

        with patch("clickloop.commands.run.validate_config"), \
             patch("clickloop.commands.run.get_monitors") as mock_get_monitors, \
             patch("clickloop.commands.run.convert_to_virtual_coords"):
            mock_get_monitors.return_value = []

            run_command(args)

            # Error may be called multiple times (no monitors, then invalid coordinates)
            assert mock_logger.error.called
            # Check that "No monitors detected" error was logged
            error_calls = [str(call) for call in mock_logger.error.call_args_list]
            assert any("No monitors detected" in str(call) for call in error_calls)
            assert mock_sys.exit.called
            assert mock_sys.exit.call_args[0][0] == 1

    @patch("clickloop.commands.run.load_config")
    @patch("clickloop.commands.run.logger")
    @patch("clickloop.commands.run.sys")
    def test_run_command_monitor_detection_fails(
        self, mock_sys, mock_logger, mock_load_config, sample_config
    ):
        """Test run command when monitor detection fails."""
        args = Mock()
        args.config = "test_config.json"
        args.loops = None
        args.wait_clicks = None
        args.wait_loops = None

        mock_load_config.return_value = sample_config

        with patch("clickloop.commands.run.validate_config"), \
             patch("clickloop.commands.run.get_monitors") as mock_get_monitors:
            mock_get_monitors.side_effect = RuntimeError("Monitor detection failed")

            run_command(args)

            # Should log the error and exit
            mock_logger.error.assert_called_once()
            assert mock_sys.exit.called
            assert mock_sys.exit.call_args[0][0] == 1

    @patch("clickloop.commands.run.load_config")
    @patch("clickloop.commands.run.logger")
    @patch("clickloop.commands.run.sys")
    def test_run_command_no_coordinates(self, mock_sys, mock_logger, mock_load_config, sample_monitors):
        """Test run command when no coordinates specified."""
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

            run_command(args)

            mock_logger.error.assert_called_once()
            mock_sys.exit.assert_called_once_with(1)

    @patch("clickloop.commands.run.load_config")
    @patch("clickloop.commands.run.logger")
    @patch("clickloop.commands.run.sys")
    def test_run_command_invalid_coordinate(
        self, mock_sys, mock_logger, mock_load_config, sample_config, sample_monitors
    ):
        """Test run command with invalid coordinate."""
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

            run_command(args)

            # Error may be called multiple times (invalid coordinate, then execution error)
            assert mock_logger.error.called
            # Check that "Invalid coordinate" error was logged
            error_calls = [str(call) for call in mock_logger.error.call_args_list]
            assert any("Invalid coordinate" in str(call) for call in error_calls)
            assert mock_sys.exit.called
            assert mock_sys.exit.call_args[0][0] == 1

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
    @patch("clickloop.commands.run.logger")
    @patch("clickloop.commands.run.sys")
    def test_run_command_click_loop_error(
        self, mock_sys, mock_logger, mock_load_config, sample_config, sample_monitors
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

            run_command(args)

            mock_logger.error.assert_called_once()
            mock_sys.exit.assert_called_once_with(1)

