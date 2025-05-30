from collections.abc import Mapping, Sequence
from math import isclose

from compyre.api import EqualFnResult, Pair, UnpackFnResult

__all__ = ["stdlib_mapping", "stdlib_number", "stdlib_object", "stdlib_sequence"]


def stdlib_mapping(p: Pair, /) -> UnpackFnResult:
    if not (isinstance(p.actual, Mapping) and isinstance(p.expected, Mapping)):
        return None

    if p.actual.keys() != p.expected.keys():
        return ValueError()

    return [
        Pair(
            index=(*p.index, k if isinstance(k, int) else str(k)),
            actual=v,
            expected=p.expected[k],
        )
        for k, v in p.actual.items()
    ]


def stdlib_sequence(p: Pair, /) -> UnpackFnResult:
    if not (
        (isinstance(p.actual, Sequence) and not isinstance(p.actual, str))
        and (isinstance(p.expected, Sequence) and not isinstance(p.expected, str))
    ):
        return None

    if len(p.actual) != len(p.expected):
        return ValueError()

    return [
        Pair(index=(*p.index, i), actual=v, expected=p.expected[i])
        for i, v in enumerate(p.actual)
    ]


def stdlib_number(
    p: Pair, /, *, rel_tol: float = 1e-9, abs_tol: float = 0.0
) -> EqualFnResult:
    if not (
        isinstance(p.actual, (int, float)) and isinstance(p.expected, (int, float))
    ):
        return None

    if isclose(p.actual, p.expected, abs_tol=abs_tol, rel_tol=rel_tol):
        return True
    else:
        return AssertionError("FIXME statistics here")


def stdlib_object(p: Pair, /) -> EqualFnResult:
    try:
        if p.actual == p.expected:
            return True
        else:
            return AssertionError(f"{p.actual!r} != {p.expected!r}")
    except Exception as result:
        return result
