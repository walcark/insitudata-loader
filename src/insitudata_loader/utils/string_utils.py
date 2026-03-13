import textwrap
import re


def dedent(text: str) -> str:
    """Remove common leading whitespace and strip surrounding newlines."""
    return textwrap.dedent(text).strip("\n")


def ensure_correct_tile_pattern(arg_value: str) -> None:
    """Catch wrong tile id patterns (ex: T31TCJ rather than 31TCJ)."""
    pat = re.compile(r"^[0-6][0-9][A-Za-z]([A-Za-z]){0,2}$")
    if not pat.match(arg_value):
        raise ValueError(f"Wrong tile pattern: {arg_value}.")
