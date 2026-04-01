from compyre import api

__all__ = ["both_isinstance", "either_isinstance"]


def both_isinstance(pair: api.Pair, t: type | tuple[type, ...], /) -> bool:
    """Check whether both values in a pair are instances of a given type.

    Args:
        pair: Pair to be checked
        t: The type or tuple of types to check the `pair`'s values against.

    Returns:
        Whether both [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are instances of `t`.

    """
    return isinstance(pair.actual, t) and isinstance(pair.expected, t)


def either_isinstance(pair: api.Pair, t: type | tuple[type, ...], /) -> bool:
    """Check whether either value in a pair is an instance of a given type.

    Args:
        pair: Pair to be checked
        t: The type or tuple of types to check the `pair`'s values against.

    Returns:
        Whether either [`p.actual`][compyre.api.Pair] or [`p.expected`][compyre.api.Pair] is an instances of `t`.

    """
    return isinstance(pair.actual, t) or isinstance(pair.expected, t)
