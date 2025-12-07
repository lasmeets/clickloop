"""Tests for pick command - coordinate picker functionality."""

from unittest.mock import Mock, patch

import pytest

from clickloop.commands.pick import pick_coordinates, pick_command


def create_get_cursor_pos_side_effect(x, y):
    """Create a side_effect for GetCursorPos that properly sets POINT coordinates.
    
    The issue is that ctypes.byref() creates a _ctypes.CArgObject that we can't
    directly modify. We access the underlying POINT structure via _obj attribute.
    """
    def side_effect(point_ptr):
        # point_ptr is a _ctypes.CArgObject from ctypes.byref(point)
        # Access the underlying POINT structure via _obj attribute
        # This is the actual POINT instance that was passed to byref()
        point = point_ptr._obj
        point.x = x
        point.y = y
        return True
    return side_effect


class TestPickCoordinates:
    """Tests for pick_coordinates function."""

    @patch("clickloop.commands.pick.save_coordinates_to_config")
    @patch("clickloop.commands.pick.get_monitor_for_point")
    @patch("clickloop.commands.pick.get_monitors")
    @patch("clickloop.commands.pick.user32")
    @patch("clickloop.commands.pick.time.sleep")
    @patch("builtins.print")
    def test_pick_coordinates_capture_via_space(
        self,
        mock_print,
        _mock_sleep,
        mock_user32,
        mock_get_monitors,
        mock_get_monitor_for_point,
        _mock_save_config,
        sample_monitors,
    ):
        """Test capturing coordinates via SPACE key."""
        # Setup mocks
        mock_get_monitors.return_value = sample_monitors
        mock_get_monitor_for_point.return_value = (0, sample_monitors[0])

        # Mock mouse position - use helper function
        mock_user32.GetCursorPos.side_effect = create_get_cursor_pos_side_effect(100, 200)

        # Mock key states: SPACE pressed on first loop iteration, ESC on second
        call_count = [0]

        def get_async_key_state(key_code):
            call_count[0] += 1
            loop_iteration = (call_count[0] - 1) // 4  # Which loop (0-indexed)
            position_in_loop = (call_count[0] - 1) % 4  # Which call in loop (0-3)
            
            if loop_iteration == 0:  # First loop - SPACE pressed
                if key_code == 0x20:  # VK_SPACE
                    return 0x8000 if position_in_loop == 0 else 0
            elif loop_iteration == 1:  # Second loop - ESC pressed to exit
                if key_code == 0x1B:  # VK_ESCAPE
                    return 0x8000 if position_in_loop == 2 else 0
            return 0

        mock_user32.GetAsyncKeyState.side_effect = get_async_key_state

        # Mock input to skip save
        with patch("builtins.input", return_value="n"):
            pick_coordinates()

        # Verify monitor detection was called
        mock_get_monitors.assert_called_once()

        # Verify coordinate was captured (check print calls for capture message)
        print_calls = [str(call) for call in mock_print.call_args_list]
        capture_calls = [call for call in print_calls if "Captured coordinate #" in call]
        assert len(capture_calls) == 1

    @patch("clickloop.commands.pick.save_coordinates_to_config")
    @patch("clickloop.commands.pick.get_monitor_for_point")
    @patch("clickloop.commands.pick.get_monitors")
    @patch("clickloop.commands.pick.user32")
    @patch("clickloop.commands.pick.time.sleep")
    @patch("builtins.print")
    def test_pick_coordinates_capture_via_enter(
        self,
        mock_print,
        _mock_sleep,
        mock_user32,
        mock_get_monitors,
        mock_get_monitor_for_point,
        _mock_save_config,
        sample_monitors,
    ):
        """Test capturing coordinates via ENTER key."""
        mock_get_monitors.return_value = sample_monitors
        mock_get_monitor_for_point.return_value = (0, sample_monitors[0])

        mock_user32.GetCursorPos.side_effect = create_get_cursor_pos_side_effect(300, 400)

        # ENTER pressed on first loop, ESC on second loop
        call_count = [0]

        def get_async_key_state(key_code):
            call_count[0] += 1
            loop_iteration = (call_count[0] - 1) // 4  # Which loop (0-indexed)
            position_in_loop = (call_count[0] - 1) % 4  # Which call in loop (0-3)

            if loop_iteration == 0:  # First loop - ENTER pressed
                if key_code == 0x0D:  # VK_RETURN
                    return 0x8000 if position_in_loop == 1 else 0
            elif loop_iteration == 1:  # Second loop - ESC pressed to exit
                if key_code == 0x1B:  # VK_ESCAPE
                    return 0x8000 if position_in_loop == 2 else 0
            return 0

        mock_user32.GetAsyncKeyState.side_effect = get_async_key_state

        with patch("builtins.input", return_value="n"):
            pick_coordinates()

        # Verify coordinate was captured
        print_calls = [str(call) for call in mock_print.call_args_list]
        capture_calls = [call for call in print_calls if "Captured coordinate #" in call]
        assert len(capture_calls) == 1

    @patch("clickloop.commands.pick.save_coordinates_to_config")
    @patch("clickloop.commands.pick.get_monitor_for_point")
    @patch("clickloop.commands.pick.get_monitors")
    @patch("clickloop.commands.pick.user32")
    @patch("clickloop.commands.pick.time.sleep")
    @patch("builtins.print")
    def test_pick_coordinates_capture_via_mouse_click(
        self,
        mock_print,
        _mock_sleep,
        mock_user32,
        mock_get_monitors,
        mock_get_monitor_for_point,
        _mock_save_config,
        sample_monitors,
    ):
        """Test capturing coordinates via mouse click."""
        mock_get_monitors.return_value = sample_monitors
        mock_get_monitor_for_point.return_value = (1, sample_monitors[1])

        mock_user32.GetCursorPos.side_effect = create_get_cursor_pos_side_effect(2000, 500)

        # Mouse button pressed on first loop, ESC on second loop
        call_count = [0]

        def get_async_key_state(key_code):
            call_count[0] += 1
            loop_iteration = (call_count[0] - 1) // 4  # Which loop (0-indexed)
            position_in_loop = (call_count[0] - 1) % 4  # Which call in loop (0-3)
            
            if loop_iteration == 0:  # First loop - Mouse button pressed
                if key_code == 0x01:  # VK_LBUTTON
                    return 0x8000 if position_in_loop == 3 else 0
            elif loop_iteration == 1:  # Second loop - ESC pressed to exit
                if key_code == 0x1B:  # VK_ESCAPE
                    return 0x8000 if position_in_loop == 2 else 0
            return 0

        mock_user32.GetAsyncKeyState.side_effect = get_async_key_state

        with patch("builtins.input", return_value="n"):
            pick_coordinates()

        # Verify coordinate was captured
        print_calls = [str(call) for call in mock_print.call_args_list]
        capture_calls = [call for call in print_calls if "Captured coordinate #" in call]
        assert len(capture_calls) == 1

    @patch("clickloop.commands.pick.get_monitors")
    @patch("builtins.print")
    def test_pick_coordinates_no_monitors_detected(
        self, _mock_print, mock_get_monitors
    ):
        """Test that RuntimeError is raised when no monitors detected."""
        mock_get_monitors.return_value = []

        with pytest.raises(RuntimeError, match="No monitors detected"):
            pick_coordinates()

    @patch("clickloop.commands.pick.get_monitors")
    def test_pick_coordinates_monitor_detection_fails(self, mock_get_monitors):
        """Test that RuntimeError is raised when monitor detection fails."""
        mock_get_monitors.side_effect = RuntimeError("Monitor detection failed")

        with pytest.raises(RuntimeError, match="Failed to detect monitors"):
            pick_coordinates()

    @patch("clickloop.commands.pick.save_coordinates_to_config")
    @patch("clickloop.commands.pick.get_monitor_for_point")
    @patch("clickloop.commands.pick.get_monitors")
    @patch("clickloop.commands.pick.user32")
    @patch("clickloop.commands.pick.time.sleep")
    @patch("builtins.print")
    def test_pick_coordinates_mouse_outside_monitors(
        self,
        mock_print,
        _mock_sleep,
        mock_user32,
        mock_get_monitors,
        mock_get_monitor_for_point,
        _mock_save_config,
        sample_monitors,
    ):
        """Test handling when mouse is outside all monitors."""
        mock_get_monitors.return_value = sample_monitors
        mock_get_monitor_for_point.return_value = (-1, None)  # Outside all monitors

        mock_user32.GetCursorPos.side_effect = create_get_cursor_pos_side_effect(-100, -100)

        # SPACE pressed (capture outside) on first loop, ESC on second loop
        call_count = [0]

        def get_async_key_state(key_code):
            call_count[0] += 1
            loop_iteration = (call_count[0] - 1) // 4  # Which loop (0-indexed)
            position_in_loop = (call_count[0] - 1) % 4  # Which call in loop (0-3)
            
            if loop_iteration == 0:  # First loop - SPACE pressed
                if key_code == 0x20:  # VK_SPACE
                    return 0x8000 if position_in_loop == 0 else 0
            elif loop_iteration == 1:  # Second loop - ESC pressed to exit
                if key_code == 0x1B:  # VK_ESCAPE
                    return 0x8000 if position_in_loop == 2 else 0
            return 0

        mock_user32.GetAsyncKeyState.side_effect = get_async_key_state

        with patch("builtins.input", return_value="n"):
            pick_coordinates()

        # Verify warning was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        warning_calls = [call for call in print_calls if "outside all monitors" in call.lower()]
        assert len(warning_calls) > 0

    @patch("clickloop.commands.pick.get_monitor_for_point")
    @patch("clickloop.commands.pick.get_monitors")
    @patch("clickloop.commands.pick.user32")
    @patch("clickloop.commands.pick.time.sleep")
    @patch("builtins.print")
    @patch("builtins.input")
    def test_pick_coordinates_keyboard_interrupt(
        self,
        mock_input,
        mock_print,
        mock_sleep,
        mock_user32,
        mock_get_monitors,
        mock_get_monitor_for_point,
        sample_monitors,
    ):
        """Test that KeyboardInterrupt is handled gracefully."""
        mock_get_monitors.return_value = sample_monitors
        mock_get_monitor_for_point.return_value = (0, sample_monitors[0])

        mock_user32.GetCursorPos.side_effect = create_get_cursor_pos_side_effect(100, 200)
        
        # Mock key states - all keys not pressed so loop doesn't exit normally
        mock_user32.GetAsyncKeyState.return_value = 0

        # Simulate KeyboardInterrupt - raise it after first sleep call (in the loop)
        call_count = [0]
        def sleep_side_effect(duration):
            call_count[0] += 1
            # Raise KeyboardInterrupt on the sleep call inside the main loop (not the early one)
            # The first sleep might be at line 92 if GetCursorPos fails, so skip that
            if call_count[0] > 1:
                raise KeyboardInterrupt()
        
        mock_sleep.side_effect = sleep_side_effect
        mock_input.return_value = "n"  # Mock input in case it gets that far

        pick_coordinates()

        # Verify exit message was printed
        # Check the actual call arguments, not just string representation
        exit_found = False
        for call in mock_print.call_args_list:
            # call is a tuple of (args, kwargs), so check args[0] if it exists
            if call.args and len(call.args) > 0:
                message = str(call.args[0])
                if "Interrupted" in message or "Exiting without saving" in message:
                    exit_found = True
                    break
        assert exit_found, f"Expected interrupt message, got calls: {mock_print.call_args_list}"

    @patch("clickloop.commands.pick.save_coordinates_to_config")
    @patch("clickloop.commands.pick.get_monitor_for_point")
    @patch("clickloop.commands.pick.get_monitors")
    @patch("clickloop.commands.pick.user32")
    @patch("clickloop.commands.pick.time.sleep")
    @patch("builtins.print")
    def test_pick_coordinates_save_to_file_with_path(
        self,
        _mock_print,
        _mock_sleep,
        mock_user32,
        mock_get_monitors,
        mock_get_monitor_for_point,
        mock_save_config,
        sample_monitors,
    ):
        """Test saving coordinates when config_path is provided."""
        mock_get_monitors.return_value = sample_monitors
        mock_get_monitor_for_point.return_value = (0, sample_monitors[0])

        mock_user32.GetCursorPos.side_effect = create_get_cursor_pos_side_effect(100, 200)

        # SPACE pressed on first loop, ESC on second loop
        call_count = [0]

        def get_async_key_state(key_code):
            call_count[0] += 1
            loop_iteration = (call_count[0] - 1) // 4  # Which loop (0-indexed)
            position_in_loop = (call_count[0] - 1) % 4  # Which call in loop (0-3)
            
            if loop_iteration == 0:  # First loop - SPACE pressed
                if key_code == 0x20:  # VK_SPACE
                    return 0x8000 if position_in_loop == 0 else 0
            elif loop_iteration == 1:  # Second loop - ESC pressed to exit
                if key_code == 0x1B:  # VK_ESCAPE
                    return 0x8000 if position_in_loop == 2 else 0
            return 0

        mock_user32.GetAsyncKeyState.side_effect = get_async_key_state

        test_config_path = "test_config.json"
        pick_coordinates(config_path=test_config_path)

        # Verify save was called with correct path
        mock_save_config.assert_called_once()
        call_args = mock_save_config.call_args
        assert call_args[0][1] == test_config_path
        assert call_args[1]["merge"] is True

    @patch("clickloop.commands.pick.save_coordinates_to_config")
    @patch("clickloop.commands.pick.get_monitor_for_point")
    @patch("clickloop.commands.pick.get_monitors")
    @patch("clickloop.commands.pick.user32")
    @patch("clickloop.commands.pick.time.sleep")
    @patch("builtins.print")
    def test_pick_coordinates_save_to_file_with_prompt(
        self,
        _mock_print,
        _mock_sleep,
        mock_user32,
        mock_get_monitors,
        mock_get_monitor_for_point,
        mock_save_config,
        sample_monitors,
    ):
        """Test saving coordinates with user prompt (default path)."""
        mock_get_monitors.return_value = sample_monitors
        mock_get_monitor_for_point.return_value = (0, sample_monitors[0])

        mock_user32.GetCursorPos.side_effect = create_get_cursor_pos_side_effect(100, 200)

        # SPACE pressed on first loop, ESC on second loop
        call_count = [0]

        def get_async_key_state(key_code):
            call_count[0] += 1
            loop_iteration = (call_count[0] - 1) // 4  # Which loop (0-indexed)
            position_in_loop = (call_count[0] - 1) % 4  # Which call in loop (0-3)
            
            if loop_iteration == 0:  # First loop - SPACE pressed
                if key_code == 0x20:  # VK_SPACE
                    return 0x8000 if position_in_loop == 0 else 0
            elif loop_iteration == 1:  # Second loop - ESC pressed to exit
                if key_code == 0x1B:  # VK_ESCAPE
                    return 0x8000 if position_in_loop == 2 else 0
            return 0

        mock_user32.GetAsyncKeyState.side_effect = get_async_key_state

        # User presses Enter (default path)
        with patch("builtins.input", return_value=""):
            pick_coordinates()

        # Verify save was called with default path
        mock_save_config.assert_called_once()
        call_args = mock_save_config.call_args
        assert call_args[0][1] == "data/config/coordinates.json"

    @patch("clickloop.commands.pick.get_monitor_for_point")
    @patch("clickloop.commands.pick.get_monitors")
    @patch("clickloop.commands.pick.user32")
    @patch("clickloop.commands.pick.time.sleep")
    @patch("builtins.print")
    def test_pick_coordinates_skip_save(
        self,
        mock_print,
        _mock_sleep,
        mock_user32,
        mock_get_monitors,
        mock_get_monitor_for_point,
        sample_monitors,
    ):
        """Test skipping save when user enters 'n'."""
        mock_get_monitors.return_value = sample_monitors
        mock_get_monitor_for_point.return_value = (0, sample_monitors[0])

        mock_user32.GetCursorPos.side_effect = create_get_cursor_pos_side_effect(100, 200)

        # SPACE pressed on first loop, ESC on second loop
        call_count = [0]

        def get_async_key_state(key_code):
            call_count[0] += 1
            loop_iteration = (call_count[0] - 1) // 4  # Which loop (0-indexed)
            position_in_loop = (call_count[0] - 1) % 4  # Which call in loop (0-3)
            
            if loop_iteration == 0:  # First loop - SPACE pressed
                if key_code == 0x20:  # VK_SPACE
                    return 0x8000 if position_in_loop == 0 else 0
            elif loop_iteration == 1:  # Second loop - ESC pressed to exit
                if key_code == 0x1B:  # VK_ESCAPE
                    return 0x8000 if position_in_loop == 2 else 0
            return 0

        mock_user32.GetAsyncKeyState.side_effect = get_async_key_state

        with patch("builtins.input", return_value="n"):
            pick_coordinates()

        # Verify skip message was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        skip_calls = [call for call in print_calls if "Skipping save" in call or "skip" in call.lower()]
        assert len(skip_calls) > 0

    @patch("clickloop.commands.pick.get_monitor_for_point")
    @patch("clickloop.commands.pick.get_monitors")
    @patch("clickloop.commands.pick.user32")
    @patch("clickloop.commands.pick.time.sleep")
    @patch("builtins.print")
    def test_pick_coordinates_no_coordinates_captured(
        self,
        mock_print,
        _mock_sleep,
        mock_user32,
        mock_get_monitors,
        mock_get_monitor_for_point,
        sample_monitors,
    ):
        """Test behavior when no coordinates are captured before ESC."""
        mock_get_monitors.return_value = sample_monitors
        mock_get_monitor_for_point.return_value = (0, sample_monitors[0])

        mock_user32.GetCursorPos.side_effect = create_get_cursor_pos_side_effect(100, 200)

        # ESC pressed immediately on first loop (no capture)
        call_count = [0]

        def get_async_key_state(key_code):
            call_count[0] += 1
            loop_iteration = (call_count[0] - 1) // 4  # Which loop (0-indexed)
            position_in_loop = (call_count[0] - 1) % 4  # Which call in loop (0-3)
            
            if loop_iteration == 0:  # First loop - ESC pressed immediately
                if key_code == 0x1B:  # VK_ESCAPE
                    return 0x8000 if position_in_loop == 2 else 0
            return 0

        mock_user32.GetAsyncKeyState.side_effect = get_async_key_state

        pick_coordinates()

        # Verify "No coordinates to save" message
        print_calls = [str(call) for call in mock_print.call_args_list]
        no_coords_calls = [call for call in print_calls if "No coordinates" in call]
        assert len(no_coords_calls) > 0

    @patch("clickloop.commands.pick.save_coordinates_to_config")
    @patch("clickloop.commands.pick.get_monitor_for_point")
    @patch("clickloop.commands.pick.get_monitors")
    @patch("clickloop.commands.pick.user32")
    @patch("clickloop.commands.pick.time.sleep")
    @patch("builtins.print")
    def test_pick_coordinates_save_error_handling(
        self,
        _mock_print,
        _mock_sleep,
        mock_user32,
        mock_get_monitors,
        mock_get_monitor_for_point,
        mock_save_config,
        sample_monitors,
    ):
        """Test that save errors are properly raised."""
        mock_get_monitors.return_value = sample_monitors
        mock_get_monitor_for_point.return_value = (0, sample_monitors[0])

        mock_user32.GetCursorPos.side_effect = create_get_cursor_pos_side_effect(100, 200)

        # SPACE pressed on first loop, ESC on second loop
        call_count = [0]

        def get_async_key_state(key_code):
            call_count[0] += 1
            loop_iteration = (call_count[0] - 1) // 4  # Which loop (0-indexed)
            position_in_loop = (call_count[0] - 1) % 4  # Which call in loop (0-3)
            
            if loop_iteration == 0:  # First loop - SPACE pressed
                if key_code == 0x20:  # VK_SPACE
                    return 0x8000 if position_in_loop == 0 else 0
            elif loop_iteration == 1:  # Second loop - ESC pressed to exit
                if key_code == 0x1B:  # VK_ESCAPE
                    return 0x8000 if position_in_loop == 2 else 0
            return 0

        mock_user32.GetAsyncKeyState.side_effect = get_async_key_state

        # Simulate save error
        mock_save_config.side_effect = OSError("Permission denied")

        with pytest.raises(OSError, match="Permission denied"):
            pick_coordinates(config_path="test.json")


class TestPickCommand:
    """Tests for pick_command function."""

    @patch("clickloop.commands.pick.pick_coordinates")
    def test_pick_command_success(self, mock_pick_coordinates):
        """Test successful execution of pick command."""
        args = Mock()
        args.config = "test_config.json"

        pick_command(args)

        mock_pick_coordinates.assert_called_once_with("test_config.json")

    @patch("clickloop.commands.pick.logger")
    @patch("clickloop.commands.pick.pick_coordinates")
    @patch("clickloop.commands.pick.sys")
    def test_pick_command_runtime_error(
        self, mock_sys, mock_pick_coordinates, mock_logger
    ):
        """Test that RuntimeError is handled and logged."""
        args = Mock()
        args.config = "test_config.json"

        mock_pick_coordinates.side_effect = RuntimeError("Monitor detection failed")

        pick_command(args)

        mock_logger.error.assert_called_once()
        mock_sys.exit.assert_called_once_with(1)

    @patch("clickloop.commands.pick.logger")
    @patch("clickloop.commands.pick.pick_coordinates")
    @patch("clickloop.commands.pick.sys")
    def test_pick_command_value_error(
        self, mock_sys, mock_pick_coordinates, mock_logger
    ):
        """Test that ValueError is handled and logged."""
        args = Mock()
        args.config = "test_config.json"

        mock_pick_coordinates.side_effect = ValueError("Invalid config")

        pick_command(args)

        mock_logger.error.assert_called_once()
        mock_sys.exit.assert_called_once_with(1)

    @patch("clickloop.commands.pick.logger")
    @patch("clickloop.commands.pick.pick_coordinates")
    @patch("clickloop.commands.pick.sys")
    def test_pick_command_os_error(
        self, mock_sys, mock_pick_coordinates, mock_logger
    ):
        """Test that OSError is handled and logged."""
        args = Mock()
        args.config = "test_config.json"

        mock_pick_coordinates.side_effect = OSError("File not found")

        pick_command(args)

        mock_logger.error.assert_called_once()
        mock_sys.exit.assert_called_once_with(1)

    @patch("clickloop.commands.pick.logger")
    @patch("clickloop.commands.pick.pick_coordinates")
    @patch("clickloop.commands.pick.sys")
    def test_pick_command_keyboard_interrupt(
        self, mock_sys, mock_pick_coordinates, mock_logger
    ):
        """Test that KeyboardInterrupt is handled gracefully."""
        args = Mock()
        args.config = "test_config.json"

        mock_pick_coordinates.side_effect = KeyboardInterrupt()

        pick_command(args)

        mock_logger.info.assert_called_once()
        mock_sys.exit.assert_called_once_with(0)
