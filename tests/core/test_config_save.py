"""Tests for configuration saving functionality."""

import json
import tempfile
from pathlib import Path

import pytest

from clickloop.core.config import load_config, save_coordinates_to_config


class TestSaveCoordinatesToConfig:
    """Tests for save_coordinates_to_config function."""

    def test_save_to_new_file_merge_false(self):
        """Test saving to a new file with merge=False."""
        coordinates = [
            {"monitor": 0, "x": 100, "y": 200},
            {"monitor": 1, "x": 300, "y": 400},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_path = f.name

        try:
            save_coordinates_to_config(coordinates, config_path, merge=False)

            # Verify file was created and contains only coordinates
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            assert "coordinates" in config
            assert len(config["coordinates"]) == 2
            assert config["coordinates"] == coordinates
        finally:
            Path(config_path).unlink()

    def test_save_to_new_file_merge_true(self):
        """Test saving to a new file with merge=True (creates new config)."""
        coordinates = [
            {"monitor": 0, "x": 100, "y": 200},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_path = f.name

        try:
            save_coordinates_to_config(coordinates, config_path, merge=True)

            # Verify file was created with defaults
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            assert "coordinates" in config
            assert len(config["coordinates"]) == 1
            assert config["coordinates"] == coordinates
            # Should have defaults (save_coordinates_to_config uses loops=3, not 10)
            assert config["loops"] == 3
            assert config["wait_between_clicks"] == 1.0
            assert config["wait_between_loops"] == 2.0
        finally:
            Path(config_path).unlink()

    def test_merge_with_existing_config(self, sample_config):
        """Test merging coordinates with existing config."""
        new_coordinates = [
            {"monitor": 0, "x": 500, "y": 600},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            config_path = f.name

        try:
            save_coordinates_to_config(new_coordinates, config_path, merge=True)

            # Verify coordinates were appended
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            assert len(config["coordinates"]) == 3  # 2 original + 1 new
            assert config["coordinates"][-1] == new_coordinates[0]
            # Original config should be preserved
            assert config["loops"] == sample_config["loops"]
            assert config["wait_between_clicks"] == sample_config["wait_between_clicks"]
        finally:
            Path(config_path).unlink()

    def test_merge_preserves_existing_coordinates(self, sample_config):
        """Test that merging preserves existing coordinates."""
        new_coordinates = [
            {"monitor": 1, "x": 700, "y": 800},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            config_path = f.name

        try:
            original_coords = sample_config["coordinates"].copy()

            save_coordinates_to_config(new_coordinates, config_path, merge=True)

            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Original coordinates should be first
            assert config["coordinates"][:2] == original_coords
            # New coordinate should be appended
            assert config["coordinates"][2] == new_coordinates[0]
        finally:
            Path(config_path).unlink()

    def test_merge_with_missing_coordinates_field(self):
        """Test merging when existing config is missing coordinates field."""
        existing_config = {
            "loops": 5,
            "wait_between_clicks": 0.5,
        }

        new_coordinates = [
            {"monitor": 0, "x": 100, "y": 200},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(existing_config, f)
            config_path = f.name

        try:
            save_coordinates_to_config(new_coordinates, config_path, merge=True)

            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            assert "coordinates" in config
            assert len(config["coordinates"]) == 1
            assert config["coordinates"] == new_coordinates
            # Other fields should be preserved
            assert config["loops"] == 5
        finally:
            Path(config_path).unlink()

    def test_save_error_invalid_json_in_existing_file(self):
        """Test that ValueError is raised when existing file has invalid JSON."""
        coordinates = [{"monitor": 0, "x": 100, "y": 200}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            config_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                save_coordinates_to_config(coordinates, config_path, merge=True)
        finally:
            Path(config_path).unlink()

    def test_save_error_file_permission_denied(self):
        """Test that OSError is raised when file cannot be written."""
        coordinates = [{"monitor": 0, "x": 100, "y": 200}]

        # Use a path that likely doesn't exist and can't be created
        # (on Windows, this might be a drive that doesn't exist)
        invalid_path = "Z:\\nonexistent\\path\\config.json"

        with pytest.raises(OSError, match="Failed to write"):
            save_coordinates_to_config(coordinates, invalid_path, merge=False)

    def test_save_empty_coordinates_list(self, sample_config):
        """Test saving empty coordinates list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            config_path = f.name

        try:
            save_coordinates_to_config([], config_path, merge=True)

            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Original coordinates should be preserved
            assert len(config["coordinates"]) == len(sample_config["coordinates"])
        finally:
            Path(config_path).unlink()

    def test_save_multiple_coordinates_at_once(self):
        """Test saving multiple coordinates in one call."""
        coordinates = [
            {"monitor": 0, "x": 100, "y": 200},
            {"monitor": 0, "x": 300, "y": 400},
            {"monitor": 1, "x": 500, "y": 600},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_path = f.name

        try:
            save_coordinates_to_config(coordinates, config_path, merge=False)

            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            assert len(config["coordinates"]) == 3
            assert config["coordinates"] == coordinates
        finally:
            Path(config_path).unlink()

    def test_save_overwrites_existing_coordinates_merge_false(self, sample_config):
        """Test that merge=False overwrites existing coordinates."""
        new_coordinates = [
            {"monitor": 0, "x": 999, "y": 999},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            config_path = f.name

        try:
            save_coordinates_to_config(new_coordinates, config_path, merge=False)

            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Should only have new coordinates, not original ones
            assert len(config["coordinates"]) == 1
            assert config["coordinates"] == new_coordinates
        finally:
            Path(config_path).unlink()

