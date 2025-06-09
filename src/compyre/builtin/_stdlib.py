from __future__ import annotations

import cmath
import dataclasses
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
    "collections_ordered_dict",
    "collections_sequence",
    "dataclasses_dataclass",
]


def collections_mapping(p: api.Pair, /) -> api.UnpackFnResult:
    """Unpack [collections.abc.Mapping][]s.

    Args:
        p: Pair to be unpacked.

    Returns:
        (None): If [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are not
            [collections.abc.Mapping][]s.
        (list[api.Pair]): The [`actual`][compyre.api.Pair] and [`expected`][compyre.api.Pair] values of each pair are
            the corresponding values of the input mappings, while the [`index`][compyre.api.Pair] is `p.index` extended
            by the corresponding key.
        (ValueError): If the keys of [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] mismatch.

    """
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
    """Unpack [collections.abc.Sequence][]s.

    Args:
        p: Pair to be unpacked.

    Returns:
        (None): If [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are not
            [collections.abc.Sequence][]s.
        (list[api.Pair]): The [`actual`][compyre.api.Pair] and [`expected`][compyre.api.Pair] values of each pair are
            the corresponding items of the input sequences, while the [`index`][compyre.api.Pair] is `p.index` extended
            by the corresponding index.
        (ValueError): If the length of [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] mismatch.

    """
    if not both_isinstance(p, Sequence) or either_isinstance(p, str):
        return None

    if (la := len(p.actual)) != (le := len(p.expected)):
        return ValueError(f"sequence length mismatches: {la} != {le}")

    return [
        api.Pair(index=(*p.index, i), actual=v, expected=p.expected[i])
        for i, v in enumerate(p.actual)
    ]


def collections_ordered_dict(p: api.Pair, /) -> api.UnpackFnResult:
    """Unpack [collections.OrderedDict][]s.

    !!! warning

        Since a [collections.OrderedDict][] is a [collections.abc.Mapping][], this function must be placed before
        [compyre.builtin.unpack_fns.collections_mapping][] or it will be shadowed.

    Args:
        p: Pair to be unpacked.

    Returns:
        (None): If [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are not
            [collections.abc.Sequence][]s.
        (list[api.Pair]): The [`actual`][compyre.api.Pair] and [`expected`][compyre.api.Pair] values of each pair are
            the corresponding values of the inputs, while the [`index`][compyre.api.Pair] is `p.index` extended
            by the corresponding key.
        (ValueError): If the ordered keys of [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair]
            mismatch.

    """
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
    """Check equality for [int][], [float][], [complex][] numbers using [math.isclose][] or [cmath.isclose][].

    Args:
        p: Pair to be compared.
        rel_tol: Relative tolerance. See [math.isclose][] or [cmath.isclose][] for details. Can also be set through
            [compyre.alias.RELATIVE_TOLERANCE][].
        abs_tol: Absolute tolerance. See [math.isclose][] or [cmath.isclose][] for details. Can also be set through
            [compyre.alias.ABSOLUTE_TOLERANCE][].

    Returns:
       (None): If [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are not [int][]s, [float][]s, or
            [complex][]s.
       (True): If [math.isclose][] or [cmath.isclose][] returns [True][] for the input pair.
       (AssertionError): If [math.isclose][] or [cmath.isclose][] returns [False][] for the input pair.

    """
    if not both_isinstance(p, (int, float, complex)) or either_isinstance(p, bool):
        return None

    isclose = cmath.isclose if either_isinstance(p, complex) else math.isclose
    if isclose(p.actual, p.expected, abs_tol=abs_tol, rel_tol=rel_tol):
        return True

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
    """Check equality for arbitrary objects.

    !!! info

        - The equality check is performed as `actual == expected`
        - The identity check is performed as `actual is expected`

    !!! warning

        This function returns a non-[None][] value for *any* input pair and thus will shadow any other equality
        function coming after it in the list of `equal_fns` in [compyre.api.compare][] or related functions.

    Args:
        p: Pair to be compared.
        identity_fallback: Whether to perform identity check of `p` if the equality check raises any [Exception][].

    Returns:
       (True): Whether the equality check, or if `identity_fallback` is set, the identity check returns [True][].
       (AssertionError): Whether the equality check, and if `identity_fallback` is set, the identity check returns
            [False][].
       (Exception): Any [Exception][] raised by the equality check if `identity_fallback` is not set.

    """
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


def dataclasses_dataclass(p: api.Pair, /) -> api.UnpackFnResult:
    """Unpack [`@dataclasses.dataclass`][dataclasses.dataclass]es using [dataclasses.asdict][].

    Args:
        p: Pair to be unpacked.

    Returns:
        (None): If [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are not
            [`@dataclasses.dataclass`][dataclasses.dataclass]es.
        (list[api.Pair]): The [`actual`][compyre.api.Pair] and [`expected`][compyre.api.Pair] values of each pair are
            the corresponding values of the input objects, while the [`index`][compyre.api.Pair] is `p.index` extended
            by the corresponding field name.
        (ValueError): If the fields of [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] mismatch.

    """
    # dataclasses.is_dataclass returns True for dataclass instances and types, but we only handle the former
    if not (
        dataclasses.is_dataclass(p.actual) and dataclasses.is_dataclass(p.expected)
    ) or either_isinstance(p, type):
        return None

    return collections_mapping(
        api.Pair(
            index=p.index,
            actual=dataclasses.asdict(p.actual),  # type: ignore[arg-type]
            expected=dataclasses.asdict(p.expected),  # type: ignore[arg-type]
        )
    )
