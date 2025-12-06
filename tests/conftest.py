"""Pytest configuration and fixtures for ClickLoop tests."""

from unittest.mock import MagicMock
from ctypes.wintypes import RECT

import pytest

from clickloop.__main__ import MonitorInfo


@pytest.fixture
def mock_user32():
    """Mock user32 Windows API."""
    return MagicMock()


@pytest.fixture
def mock_gdi32():
    """Mock gdi32 Windows API."""
    return MagicMock()


@pytest.fixture
def sample_monitors():
    """Sample monitor data for testing."""
    # Create mock RECT structures
    monitor1_bounds = RECT()
    monitor1_bounds.left = 0
    monitor1_bounds.top = 0
    monitor1_bounds.right = 1920
    monitor1_bounds.bottom = 1080

    monitor2_bounds = RECT()
    monitor2_bounds.left = 1920
    monitor2_bounds.top = 0
    monitor2_bounds.right = 3840
    monitor2_bounds.bottom = 1080

    monitors = [
        MonitorInfo(None, monitor1_bounds, True),  # Primary monitor
        MonitorInfo(None, monitor2_bounds, False),  # Secondary monitor
    ]
    return monitors


@pytest.fixture
def sample_config():
    """Sample configuration dictionary."""
    return {
        "loops": 5,
        "wait_between_clicks": 0.5,
        "wait_between_loops": 1.0,
        "coordinates": [
            {"monitor": 0, "x": 100, "y": 200},
            {"monitor": 1, "x": 300, "y": 400},
        ],
    }


@pytest.fixture
def sample_config_minimal():
    """Minimal configuration dictionary."""
    return {
        "coordinates": [
            {"monitor": 0, "x": 50, "y": 50},
        ],
    }
