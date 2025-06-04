from __future__ import annotations

import cmath
import math
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from typing import Annotated

from compyre import alias, api

from ._utils import both_isinstance, either_isinstance

__all__ = [
    "builtins_number",
    "builtins_object",
    "collections_mapping",
    "collections_sequence",
]


def collections_mapping(p: api.Pair, /) -> api.UnpackFnResult:
    if not both_isinstance(p, Mapping):
        return None

    extra = p.actual.keys() - p.expected.keys()
    missing = p.expected.keys() - p.actual.keys()
    if extra or missing:
        return ValueError(
            f"mapping keys mismatch:\n\n"
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
    if not both_isinstance(p, Sequence) or either_isinstance(p, str):
        return None

    if (la := len(p.actual)) != (le := len(p.expected)):
        return ValueError(f"sequence length mismatches: {la} != {le}")

    return [
        api.Pair(index=(*p.index, i), actual=v, expected=p.expected[i])
        for i, v in enumerate(p.actual)
    ]


def collections_ordered_dict(p: api.Pair, /) -> api.UnpackFnResult:
    if not both_isinstance(p, OrderedDict):
        return None

    if (aks := list(p.actual.keys())) != (eks := list(p.expected.keys())):
        return ValueError(f"ordered keys mismatch: {list(aks)} != {list(eks)}")

    return [
        api.Pair(
            index=(*p.index, k if isinstance(k, int) else str(k)),
            actual=v,
            expected=p.expected[k],
        )
        for k, v in p.actual.items()
    ]


def builtins_number(
    p: api.Pair,
    /,
    *,
    rel_tol: Annotated[float, alias.RELATIVE_TOLERANCE] = 1e-9,
    abs_tol: Annotated[float, alias.ABSOLUTE_TOLERANCE] = 0.0,
) -> api.EqualFnResult:
    if not both_isinstance(p, (int, float, complex)) or either_isinstance(p, bool):
        return None

    isclose = cmath.isclose if either_isinstance(p, complex) else math.isclose
    if isclose(p.actual, p.expected, abs_tol=abs_tol, rel_tol=rel_tol):
        return True
    else:

        def diff_msg(*, typ: str, diff: float, tol: float) -> str:
            msg = f"{typ.title()} difference: {diff}"
            if tol > 0:
                msg += f" (up to {tol} allowed)"
            return msg

        equality = rel_tol == 0 and abs_tol == 0
        abs_diff = abs(p.actual - p.expected)
        rel_diff = abs_diff / max(abs(p.actual), abs(p.expected))

        return AssertionError(
            "\n".join(
                [
                    f"Numbers {p.actual} and {p.expected} are not {'equal' if equality else 'close'}!\n",
                    diff_msg(typ="absolute", diff=abs_diff, tol=abs_tol),
                    diff_msg(typ="relative", diff=rel_diff, tol=rel_tol),
                ]
            )
        )


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
