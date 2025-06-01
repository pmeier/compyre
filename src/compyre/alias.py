class Alias:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{type(self).__module__}.{type(self).__name__}({self!s})"


RELATIVE_TOLERANCE = Alias("relative_tolerance")
ABSOLUTE_TOLERANCE = Alias("absolute_tolerance")
