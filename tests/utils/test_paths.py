"""Tests for path utilities."""

import os
from pathlib import Path

from clickloop.utils.paths import (
    get_package_config_dir,
    get_package_data_dir,
    get_package_logs_dir,
)


class TestPackagePathResolution:
    """Tests for package path resolution to ensure data/logs/config are in package directory."""

    def test_get_package_data_dir_returns_absolute_path(self):
        """Test that data directory path is absolute."""
        data_dir = get_package_data_dir()

        assert isinstance(data_dir, Path)
        assert data_dir.is_absolute()

    def test_get_package_data_dir_contains_data_folder(self):
        """Test that returned path ends with 'data' directory."""
        data_dir = get_package_data_dir()

        assert data_dir.name == "data"

    def test_get_package_data_dir_relative_to_package_root(self):
        """Test that data directory is at package root, not current working directory."""
        data_dir = get_package_data_dir()

        # Data dir should be under the package root, not the current working directory
        package_root = Path(__file__).parent.parent.parent / "src" / "clickloop"
        expected_data_dir = package_root.parent.parent / "data"

        assert data_dir == expected_data_dir

    def test_get_package_config_dir_returns_absolute_path(self):
        """Test that config directory path is absolute."""
        config_dir = get_package_config_dir()

        assert isinstance(config_dir, Path)
        assert config_dir.is_absolute()

    def test_get_package_config_dir_path_structure(self):
        """Test that config directory is data/config."""
        config_dir = get_package_config_dir()

        assert config_dir.parent.name == "data"
        assert config_dir.name == "config"

    def test_get_package_config_dir_relative_to_data_dir(self):
        """Test that config directory is under data directory."""
        config_dir = get_package_config_dir()
        data_dir = get_package_data_dir()

        assert config_dir.parent == data_dir

    def test_get_package_logs_dir_returns_absolute_path(self):
        """Test that logs directory path is absolute."""
        logs_dir = get_package_logs_dir()

        assert isinstance(logs_dir, Path)
        assert logs_dir.is_absolute()

    def test_get_package_logs_dir_path_structure(self):
        """Test that logs directory is data/logs."""
        logs_dir = get_package_logs_dir()

        assert logs_dir.parent.name == "data"
        assert logs_dir.name == "logs"

    def test_get_package_logs_dir_relative_to_data_dir(self):
        """Test that logs directory is under data directory."""
        logs_dir = get_package_logs_dir()
        data_dir = get_package_data_dir()

        assert logs_dir.parent == data_dir

    def test_paths_independent_of_cwd(self):
        """Test that paths are resolved correctly regardless of current working directory."""
        # Get paths in current directory
        original_cwd = os.getcwd()
        data_dir_current = get_package_data_dir()
        config_dir_current = get_package_config_dir()
        logs_dir_current = get_package_logs_dir()

        try:
            # Change to user home directory (safe to change to)
            home_dir = os.path.expanduser("~")
            os.chdir(home_dir)

            # Get paths from different directory
            data_dir_tmp = get_package_data_dir()
            config_dir_tmp = get_package_config_dir()
            logs_dir_tmp = get_package_logs_dir()

            # Paths should be the same regardless of cwd
            assert data_dir_current == data_dir_tmp
            assert config_dir_current == config_dir_tmp
            assert logs_dir_current == logs_dir_tmp
        finally:
            os.chdir(original_cwd)

    def test_all_paths_under_same_package_root(self):
        """Test that all paths are under the same package root."""
        data_dir = get_package_data_dir()
        config_dir = get_package_config_dir()
        logs_dir = get_package_logs_dir()

        # All should have data as a parent (or be data)
        assert "data" in str(data_dir)
        assert "data" in str(config_dir)
        assert "data" in str(logs_dir)

        # Config and logs should be children of data
        assert config_dir.parent == data_dir
        assert logs_dir.parent == data_dir

    def test_paths_not_relative_paths(self):
        """Test that no paths are relative (e.g., starting with 'data/')."""
        data_dir = str(get_package_data_dir())
        config_dir = str(get_package_config_dir())
        logs_dir = str(get_package_logs_dir())

        # None should start with 'data/' or '.\data'
        assert not data_dir.startswith("data")
        assert not config_dir.startswith("data")
        assert not logs_dir.startswith("data")

        # Should not start with relative path markers
        assert not data_dir.startswith("." + os.sep)
        assert not config_dir.startswith("." + os.sep)
        assert not logs_dir.startswith("." + os.sep)

    def test_coordinates_json_path_construction(self):
        """Test constructing full path to coordinates.json."""
        config_dir = get_package_config_dir()
        coordinates_json = config_dir / "coordinates.json"

        assert isinstance(coordinates_json, Path)
        assert coordinates_json.is_absolute()
        assert coordinates_json.name == "coordinates.json"
        assert coordinates_json.parent == config_dir

    def test_symlink_resolution(self):
        """Test that paths handle symlinks (using resolve())."""
        data_dir = get_package_data_dir()

        # The path should be resolved (no symlinks or relative components like ..)
        assert data_dir == data_dir.resolve()
