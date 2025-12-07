"""Tests for configuration loading and validation."""

import json
import tempfile
from pathlib import Path

import pytest

from clickloop.core.config import load_config, validate_config


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, sample_config):
        """Test loading a valid configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            config_path = f.name

        try:
            config = load_config(config_path)
            assert config["loops"] == 5
            assert config["wait_between_clicks"] == 0.5
            assert config["wait_between_loops"] == 1.0
            assert len(config["coordinates"]) == 2
        finally:
            Path(config_path).unlink()

    def test_load_config_with_defaults(self):
        """Test loading config with missing fields uses defaults."""
        minimal_config = {
            "coordinates": [
                {"monitor": 0, "x": 100, "y": 200},
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(minimal_config, f)
            config_path = f.name

        try:
            config = load_config(config_path)
            assert config["loops"] == 10  # Default
            assert config["wait_between_clicks"] == 1.0  # Default
            assert config["wait_between_loops"] == 2.0  # Default
            assert len(config["coordinates"]) == 1
        finally:
            Path(config_path).unlink()

    def test_load_config_missing_file(self):
        """Test loading non-existent config file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_file.json")

    def test_load_config_invalid_json(self):
        """Test loading invalid JSON raises ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            config_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                load_config(config_path)
        finally:
            Path(config_path).unlink()


class TestValidateConfig:
    """Tests for validate_config function."""

    def test_validate_valid_config(self, sample_config):
        """Test validating a valid configuration."""
        validate_config(sample_config)  # Should not raise

    def test_validate_minimal_config(self, sample_config_minimal):
        """Test validating minimal valid configuration."""
        validate_config(sample_config_minimal)  # Should not raise

    def test_validate_invalid_loops_type(self):
        """Test validation fails for invalid loops type."""
        config = {
            "loops": "not an int",
            "coordinates": [{"monitor": 0, "x": 100, "y": 200}],
        }
        with pytest.raises(ValueError, match="loops must be a positive integer"):
            validate_config(config)

    def test_validate_invalid_loops_value(self):
        """Test validation fails for invalid loops value."""
        config = {
            "loops": 0,
            "coordinates": [{"monitor": 0, "x": 100, "y": 200}],
        }
        with pytest.raises(ValueError, match="loops must be a positive integer"):
            validate_config(config)

    def test_validate_invalid_wait_between_clicks(self):
        """Test validation fails for invalid wait_between_clicks."""
        config = {
            "wait_between_clicks": -1,
            "coordinates": [{"monitor": 0, "x": 100, "y": 200}],
        }
        with pytest.raises(ValueError, match="wait_between_clicks must be a non-negative number"):
            validate_config(config)

    def test_validate_invalid_wait_between_loops(self):
        """Test validation fails for invalid wait_between_loops."""
        config = {
            "wait_between_loops": -1,
            "coordinates": [{"monitor": 0, "x": 100, "y": 200}],
        }
        with pytest.raises(ValueError, match="wait_between_loops must be a non-negative number"):
            validate_config(config)

    def test_validate_missing_coordinates(self):
        """Test validation fails when coordinates are missing."""
        config = {
            "loops": 5,
        }
        with pytest.raises(ValueError, match="coordinates must be a list"):
            validate_config(config)

    def test_validate_coordinates_not_list(self):
        """Test validation fails when coordinates is not a list."""
        config = {
            "coordinates": "not a list",
        }
        with pytest.raises(ValueError, match="coordinates must be a list"):
            validate_config(config)

    def test_validate_empty_coordinates(self):
        """Test validation fails when coordinates list is empty."""
        config = {
            "coordinates": [],
        }
        with pytest.raises(ValueError, match="At least one coordinate must be specified"):
            validate_config(config)

    def test_validate_coordinate_not_dict(self):
        """Test validation fails when coordinate is not a dictionary."""
        config = {
            "coordinates": ["not a dict"],
        }
        with pytest.raises(ValueError, match="Coordinate 0 must be a dictionary"):
            validate_config(config)

    def test_validate_coordinate_missing_monitor(self):
        """Test validation fails when monitor field is missing."""
        config = {
            "coordinates": [{"x": 100, "y": 200}],
        }
        with pytest.raises(ValueError, match="Coordinate 0 missing 'monitor' field"):
            validate_config(config)

    def test_validate_coordinate_missing_x(self):
        """Test validation fails when x field is missing."""
        config = {
            "coordinates": [{"monitor": 0, "y": 200}],
        }
        with pytest.raises(ValueError, match="Coordinate 0 missing 'x' field"):
            validate_config(config)

    def test_validate_coordinate_missing_y(self):
        """Test validation fails when y field is missing."""
        config = {
            "coordinates": [{"monitor": 0, "x": 100}],
        }
        with pytest.raises(ValueError, match="Coordinate 0 missing 'y' field"):
            validate_config(config)

    def test_validate_invalid_monitor_type(self):
        """Test validation fails for invalid monitor type."""
        config = {
            "coordinates": [{"monitor": "not an int", "x": 100, "y": 200}],
        }
        with pytest.raises(ValueError, match="monitor must be a non-negative integer"):
            validate_config(config)

    def test_validate_invalid_monitor_value(self):
        """Test validation fails for negative monitor index."""
        config = {
            "coordinates": [{"monitor": -1, "x": 100, "y": 200}],
        }
        with pytest.raises(ValueError, match="monitor must be a non-negative integer"):
            validate_config(config)

    def test_validate_invalid_x_type(self):
        """Test validation fails for invalid x coordinate type."""
        config = {
            "coordinates": [{"monitor": 0, "x": "not a number", "y": 200}],
        }
        with pytest.raises(ValueError, match="x must be a non-negative number"):
            validate_config(config)

    def test_validate_invalid_x_value(self):
        """Test validation fails for negative x coordinate."""
        config = {
            "coordinates": [{"monitor": 0, "x": -1, "y": 200}],
        }
        with pytest.raises(ValueError, match="x must be a non-negative number"):
            validate_config(config)

    def test_validate_invalid_y_type(self):
        """Test validation fails for invalid y coordinate type."""
        config = {
            "coordinates": [{"monitor": 0, "x": 100, "y": "not a number"}],
        }
        with pytest.raises(ValueError, match="y must be a non-negative number"):
            validate_config(config)

    def test_validate_invalid_y_value(self):
        """Test validation fails for negative y coordinate."""
        config = {
            "coordinates": [{"monitor": 0, "x": 100, "y": -1}],
        }
        with pytest.raises(ValueError, match="y must be a non-negative number"):
            validate_config(config)
