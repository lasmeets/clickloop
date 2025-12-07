"""Core functionality for clickloop."""

from clickloop.core.clicking import click_at, convert_to_virtual_coords
from clickloop.core.config import (
    load_config,
    save_coordinates_to_config,
    validate_config,
)
from clickloop.core.monitors import (
    MonitorInfo,
    get_monitor_for_point,
    get_monitors,
    print_monitor_info,
)

__all__ = [
    "click_at",
    "convert_to_virtual_coords",
    "load_config",
    "save_coordinates_to_config",
    "validate_config",
    "MonitorInfo",
    "get_monitor_for_point",
    "get_monitors",
    "print_monitor_info",
]

