from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isclose
from typing import Annotated

from compyre import alias, api

from ._utils import both_isinstance

__all__ = [
    "builtins_object",
    "collections_mapping",
    "collections_sequence",
    "stdlib_number",
]


def collections_mapping(p: api.Pair, /) -> api.UnpackFnResult:
    if not both_isinstance(p, Mapping):
        return None

    extra = p.actual.keys() - p.expected.keys()
    missing = p.expected.keys() - p.actual.keys()
    if extra or missing:
        return ValueError(
            f"actual mapping keys mismatch expected:\n\n"
            f"extra: {', '.join(repr(k) for k in sorted(extra))}\n"
            f"missing: {', '.join(repr(k) for k in sorted(missing))}\n"
        )

    return [
        api.Pair(
            index=(*p.index, k if isinstance(k, int) else str(k)),
            actual=v,
            expected=p.expected[k],
        )
        for k, v in p.actual.items()
    ]


def collections_sequence(p: api.Pair, /) -> api.UnpackFnResult:
    if (
        not both_isinstance(p, Sequence)
        or isinstance(p.actual, str)
        or isinstance(p.expected, str)
    ):
        return None

    if (la := len(p.actual)) != (le := len(p.expected)):
        return ValueError(f"actual sequence length mismatches expected: {la} != {le}")

    return [
        api.Pair(index=(*p.index, i), actual=v, expected=p.expected[i])
        for i, v in enumerate(p.actual)
    ]


def stdlib_number(
    p: api.Pair,
    /,
    *,
    rel_tol: Annotated[float, alias.RELATIVE_TOLERANCE] = 1e-9,
    abs_tol: Annotated[float, alias.ABSOLUTE_TOLERANCE] = 0.0,
) -> api.EqualFnResult:
    if not both_isinstance(p, (int, float)):
        return None

    if isclose(p.actual, p.expected, abs_tol=abs_tol, rel_tol=rel_tol):
        return True
    else:
        return AssertionError("FIXME statistics here")


def builtins_object(
    p: api.Pair, /, *, identity_fallback: bool = True
) -> api.EqualFnResult:
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
