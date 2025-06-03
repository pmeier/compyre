from compyre.api import Pair

__all__ = ["both_isinstance", "either_isinstance"]


def both_isinstance(pair: Pair, t: type | tuple[type, ...]) -> bool:
    return isinstance(pair.actual, t) and isinstance(pair.expected, t)


def either_isinstance(pair: Pair, t: type | tuple[type, ...]) -> bool:
    return isinstance(pair.actual, t) or isinstance(pair.expected, t)
