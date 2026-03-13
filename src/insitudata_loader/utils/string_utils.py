import textwrap


def dedent(text: str) -> str:
    """Remove common leading whitespace and strip surrounding newlines."""
    return textwrap.dedent(text).strip("\n")
