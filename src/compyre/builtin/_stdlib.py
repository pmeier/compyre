from collections.abc import Mapping, Sequence
from math import isclose

from compyre.api import EqualFnResult, Pair, UnpackFnResult

from ._utils import both_isinstance

__all__ = [
    "builtins_object",
    "collections_mapping",
    "collections_sequence",
    "stdlib_number",
]


def collections_mapping(p: Pair, /) -> UnpackFnResult:
    if not both_isinstance(p, Mapping):
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


def collections_sequence(p: Pair, /) -> UnpackFnResult:
    if (
        not both_isinstance(p, Sequence)
        or isinstance(p.actual, str)
        or isinstance(p.expected, str)
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
    if not both_isinstance(p, (int, float)):
        return None

    if isclose(p.actual, p.expected, abs_tol=abs_tol, rel_tol=rel_tol):
        return True
    else:
        return AssertionError("FIXME statistics here")


def builtins_object(p: Pair, /, *, identity_fallback: bool = True) -> EqualFnResult:
    try:
        if p.actual == p.expected:
            return True
        else:
            return AssertionError(f"{p.actual!r} != {p.expected!r}")
    except Exception as result:
        if not identity_fallback:
            return result

        if p.actual is p.expected:
            return True
        else:
            return AssertionError(f"{p.actual!r} is not {p.expected!r}")
