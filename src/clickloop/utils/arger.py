"""This module provides coloured output support for argparse.

It defines:
- Color: Enum of plain ANSI color codes
- ColourHelpFormatter: HelpFormatter that injects colour into usage, section
  headings and option strings
- _colourise: helper that wraps text in ANSI escape sequences

"""

import re
import argparse
from enum import Enum
from typing import Optional


# ANSI color codes
class Color(str, Enum):
    """ANSI color codes."""
    RED     = "31"
    GREEN   = "32"
    YELLOW  = "33"
    BLUE    = "34"
    MAGENTA = "35"
    CYAN    = "36"
    WHITE   = "37"
    GREY    = "90"
    SAGE    = "38;5;108"
    ROSE    = "38;5;167"
    LILAC   = "38;5;141"


def _colourise(text: str, colour_code: Optional[Color]) -> str:
    """Return *text* wrapped in ANSI colour sequence if *colour_code* given."""
    if colour_code is None:
        return text
    return f"\x1b[{colour_code.value}m{text}\x1b[0m"


class ColourHelpFormatter(argparse.HelpFormatter):
    """HelpFormatter that adds colour to key parts of the help output."""

    def start_section(self, heading: str) -> None:  # type: ignore[override]
        # Section headings such as "optional arguments:" or "positional arguments:"
        coloured_heading = _colourise(heading, Color.GREEN)
        super().start_section(coloured_heading)

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = _colourise('usage:', Color.GREEN) + ' '
        super().add_usage(usage, actions, groups, prefix)

    # Colour option strings ("-m", "--model")
    def _format_action_invocation(self, action: argparse.Action) -> str:
        # Positional arguments – keep default behaviour
        if not action.option_strings:
            return super()._format_action_invocation(action)

        # Colour each option flag
        parts = [_colourise(flag, Color.CYAN) for flag in action.option_strings]

        # Append metavar if the option expects an argument
        if action.nargs != 0:
            metavar = self._format_args(action, action.dest.upper())
            parts[-1] = f"{parts[-1]} {metavar}"
        return ", ".join(parts)

    def _format_args(self, action, default_metavar):
        # Let the base class build whatever text it wants…
        text = super()._format_args(action, default_metavar)
        # …then wrap it in colour
        return _colourise(text, Color.GREY)

    # Colour default values in help text
    def _get_help_string(self, action: argparse.Action) -> str:  # noqa: N802
        """Return help string with coloured default values (if any)."""
        help_text = super()._get_help_string(action)
        # Regex to find '(default: something)' pattern
        match = re.search(r"\(default: ([^)]+)\)", help_text)
        if match:
            value = match.group(1)
            coloured_value = _colourise(value, Color.YELLOW)
            help_text = help_text.replace(match.group(0), f"(default: {coloured_value})")
        return help_text
