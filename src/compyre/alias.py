__all__ = ["ABSOLUTE_TOLERANCE", "NAN_EQUALITY", "RELATIVE_TOLERANCE", "Alias"]


class Alias:
    """
    asda

    Args:
        name: Name of the alias for debugging.

    """

    def __init__(self, name: str = "") -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{type(self).__module__}.{type(self).__name__}({self!s})"


RELATIVE_TOLERANCE = Alias("relative_tolerance")
"""Alias for relative tolerances in numerical comparisons."""

ABSOLUTE_TOLERANCE = Alias("absolute_tolerance")
"""Alias for absolute tolerances in numerical comparisons."""

NAN_EQUALITY = Alias("nan_equality")
"""Alias for NaN equality checking in numerical comparisons."""
