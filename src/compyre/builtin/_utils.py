from compyre.api import Pair

__all__ = ["both_isinstance"]


def both_isinstance(pair: Pair, t: type | tuple[type, ...]) -> bool:
    return isinstance(pair.actual, t) and isinstance(pair.expected, t)
