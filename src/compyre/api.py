from __future__ import annotations

import dataclasses
import functools
import inspect
import typing
from collections import deque
from collections.abc import Mapping, Sequence
from textwrap import indent
from typing import Any, Callable, Deque, TypeVar

from compyre.alias import Alias

__all__ = [
    "CompareError",
    "EqualFnResult",
    "Pair",
    "UnpackFnResult",
    "assert_equal",
    "compare",
    "is_equal",
]

T = TypeVar("T")


@dataclasses.dataclass
class Pair:
    """Pair of values to be unpacked or compared for equality with position information

    Attributes:
        index: Position of the pair in the overall comparison.
        actual: Actual value.
        expected: Expected value.
    """

    index: tuple[str | int, ...]
    actual: Any
    expected: Any


UnpackFnResult = Sequence[Pair] | None | Exception
"""Return type of an unpacking function

- [None][] indicates that the function cannot handle the input [compyre.api.Pair][].
- Any [Exception][] indicates that the function can generally handle the input [compyre.api.Pair][], but something is
  wrong.
"""
EqualFnResult = bool | None | Exception
"""Return type of an equality function

- [None][] indicates that the equality function cannot handle the input [compyre.api.Pair][].
- [True][] indicates that the input [compyre.api.Pair][] is equal.
- Both [False][] and any [Exception][] indicate that the input [compyre.api.Pair][] is not equal, with the latter being
  able to convey the reason.
"""


@dataclasses.dataclass
class CompareError:
    """Comparison exception with position information"""

    index: tuple[str | int, ...]
    exception: Exception


class CompyreError(Exception):
    """Exception base class for errors originating from compyre"""

    pass


def compare(
    actual: Any,
    expected: Any,
    *,
    unpack_fns: Sequence[Callable[..., UnpackFnResult]],
    equal_fns: Sequence[Callable[..., EqualFnResult]],
    aliases: Mapping[Alias, Any] | None = None,
    **kwargs: Any,
) -> list[CompareError]:
    """Low-level comparison function of the input

    The `unpack_fns` and `equal_fns` are applied depth-first to the inputs.

    Args:
        actual: Actual input.
        expected: Expected input.
        unpack_fns: Unpacking functions to be used on the inputs. See note below for acceptable signatures.
        equal_fns: Equality functions to be used on the inputs. See note below for acceptable signatures. If a falsy
                   value is returned, it will be replaced by an [AssertionError][] with a default message.
        aliases: Aliases and values to be passed to the `unpack_fns` and `equal_fns`.
        **kwargs: Keyword arguments to be passed to the `unpack_fns` and `equal_fns`.

    !!! note

        The `unpack_fns` and `equal_fns` have to be callable with a single [compyre.api.Pair][] as positional argument
        as well as optionally keyword arguments that will be set by the `aliases` and `kwargs`.

    Returns:
        List of all exceptions *returned and not raised* by the `unpack_fns` and `equal_fns` with the index of the
            corresponding [compyre.api.Pair][]. If all `unpack_fns` and `equal_fns` return `None`, i.e. cannot handle
            it, a [compyre.api.CompyreError][] is included.

    Raises:
        TypeError: If the `unpack_fns` and `equal_fns` cannot be called as described above.
        TypeError: If any parameter of the `unpack_fns` and `equal_fns` has no default, but no value was passed through
                   `aliases` or `kwargs`.
        TypeError: If any value passed to `aliases` or `kwargs` is unused by the `unpack_fns` and `equal_fns`.
    """
    parametrized_unpack_fns, parametrized_equal_fns = _parametrize_fns(
        unpack_fns=unpack_fns,
        equal_fns=equal_fns,
        kwargs=kwargs,
        aliases=aliases if aliases is not None else {},
    )

    pairs: Deque[Pair] = deque([Pair(index=(), actual=actual, expected=expected)])
    errors: list[CompareError] = []
    while pairs:
        pair = pairs.popleft()

        unpack_result: UnpackFnResult = None
        for ufn in parametrized_unpack_fns:
            unpack_result = ufn(pair)
            if unpack_result is not None:
                break

        if unpack_result is not None:
            if isinstance(unpack_result, Exception):
                errors.append(CompareError(index=pair.index, exception=unpack_result))
            else:
                for p in reversed(unpack_result):
                    pairs.appendleft(p)
            continue

        equal_result: EqualFnResult = None
        for efn in parametrized_equal_fns:
            equal_result = efn(pair)
            if equal_result is not None:
                break

        if equal_result is None:
            equal_result = CompyreError(
                f"unable to compare {pair.actual!r} of type {type(pair.actual)} "
                f"and {pair.expected!r} of type {type(pair.expected)}"
            )
        elif not equal_result:
            equal_result = AssertionError(
                f"{pair.actual!r} is not equal to {pair.expected!r}"
            )

        if isinstance(equal_result, Exception):
            errors.append(CompareError(index=pair.index, exception=equal_result))

    return errors


def _parametrize_fns(
    *,
    unpack_fns: Sequence[Callable[..., UnpackFnResult]],
    equal_fns: Sequence[Callable[..., EqualFnResult]],
    kwargs: Mapping[str, Any],
    aliases: Mapping[Alias, Any],
) -> tuple[
    list[Callable[[Pair], UnpackFnResult]], list[Callable[[Pair], EqualFnResult]]
]:
    bound: set[str | Alias] = set()

    def parametrize(fns: Sequence[Callable[..., T]]) -> list[Callable[[Pair], T]]:
        parametrized_fns: list[Callable[[Pair], T]] = []
        for fn in fns:
            pfn, b = _bind_kwargs(fn, kwargs, aliases)
            parametrized_fns.append(pfn)
            bound.update(b)

        return parametrized_fns

    parametrized_unpack_fns = parametrize(unpack_fns)
    parametrized_equal_fns = parametrize(equal_fns)

    extra_kwargs = kwargs.keys() - bound
    extra_aliases = aliases.keys() - bound
    if extra_kwargs or extra_aliases:
        parts = []
        if extra_kwargs:
            parts.append(
                f"unexpected keyword argument(s) {', '.join(repr(e) for e in sorted(extra_kwargs))}"
            )
        if extra_aliases:
            parts.append(
                f"unexpected alias(es) {', '.join(repr(e) for e in sorted(extra_aliases, key=str))}"
            )
        raise TypeError("\n".join(parts))

    return parametrized_unpack_fns, parametrized_equal_fns


def _bind_kwargs(
    fn: Callable[..., T], kwargs: Mapping[str, Any], aliases: Mapping[Alias, Any]
) -> tuple[Callable[[Pair], T], set[str | Alias]]:
    available_kwargs, available_aliases, required_kwargs = _parse_fn(fn)

    bind_kwargs = {k: v for k, v in kwargs.items() if k in available_kwargs}
    bound: set[str | Alias] = set(bind_kwargs.keys())
    for a, v in aliases.items():
        k = available_aliases.get(a)
        if k is None or k in bind_kwargs:
            continue

        bind_kwargs[k] = v
        bound.add(a)

    missing = required_kwargs - bind_kwargs.keys()
    if missing:
        raise TypeError(
            f"missing {len(missing)} keyword-only argument(s): "
            f"{', '.join(repr(m) for m in sorted(missing))}"
        )

    return functools.partial(fn, **bind_kwargs), bound


@functools.cache
def _parse_fn(fn: Callable) -> tuple[set[str], dict[Alias, str], set[str]]:
    params = list(
        inspect.signature(fn, follow_wrapped=True, eval_str=True).parameters.values()
    )
    if not params:
        raise TypeError(
            f"{fn} takes no arguments, but has to take at least one positional"
        )

    pair_arg, *params = params
    if pair_arg.kind not in {
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    }:
        raise TypeError(
            f"{fn} takes the 1. argument as {pair_arg.kind.description}, but it has to allow positional"
        )

    available: set[str] = set()
    aliases: dict[Alias, str] = {}
    required: set[str] = set()
    for i, p in enumerate(params, 2):
        if p.kind not in {
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }:
            raise TypeError(
                f"{fn} takes the {i}. argument as {p.kind.description}, but it has to allow keyword"
            )
        available.add(p.name)

        if (a := _extract_alias(p)) is not None:
            aliases[a] = p.name

        if p.default is inspect.Parameter.empty:
            required.add(p.name)

    return available, aliases, required


def _extract_alias(p: inspect.Parameter) -> Alias | None:
    if p.annotation is inspect.Parameter.empty:
        return None

    for a in typing.get_args(p.annotation)[1:]:
        if isinstance(a, Alias):
            return a

    return None


def is_equal(
    actual: Any,
    expected: Any,
    *,
    unpack_fns: Sequence[Callable[..., UnpackFnResult]],
    equal_fns: Sequence[Callable[..., EqualFnResult]],
    aliases: Mapping[Alias, Any] | None = None,
    **kwargs: Any,
) -> bool:
    """Boolean equality check of the inputs

    !!! info

        See [compyre.api.compare][] for a description of the arguments.

    Returns:
        Whether the inputs are equal.

    Raises:
        CompyreError: If any input pair cannot be handled.
        Exception: Any exception raised by [compyre.api.compare][].
    """
    return not _extract_equal_errors(
        compare(
            actual,
            expected,
            unpack_fns=unpack_fns,
            equal_fns=equal_fns,
            aliases=aliases,
            **kwargs,
        )
    )


def assert_equal(
    actual: Any,
    expected: Any,
    *,
    unpack_fns: Sequence[Callable[..., UnpackFnResult]],
    equal_fns: Sequence[Callable[..., EqualFnResult]],
    aliases: Mapping[Alias, Any] | None = None,
    **kwargs: Any,
) -> None:
    """Equality assertion of the inputs

    !!! info

        See [compyre.api.compare][] for a description of the arguments.

    Raises:
        CompyreError: If any input pair cannot be handled.
        AssertionError: If any input pair is not equal.
        Exception: Any exception raised by [compyre.api.compare][].
    """

    equal_errors = _extract_equal_errors(
        compare(
            actual,
            expected,
            unpack_fns=unpack_fns,
            equal_fns=equal_fns,
            aliases=aliases,
            **kwargs,
        )
    )
    if not equal_errors:
        return None

    raise AssertionError(
        f"comparison resulted in {len(equal_errors)} error(s):\n\n{_format_compare_errors(equal_errors)}"
    )


def _extract_equal_errors(errors: list[CompareError]) -> list[CompareError]:
    equal_errors: list[CompareError] = []
    compyre_errors: list[CompareError] = []
    for e in errors:
        (
            compyre_errors if isinstance(e.exception, CompyreError) else equal_errors
        ).append(e)

    if compyre_errors:
        raise CompyreError(_format_compare_errors(compyre_errors))

    return equal_errors


def _format_compare_errors(errors: list[CompareError]) -> str:
    parts = []
    for e in errors:
        i = ".".join(map(str, e.index))
        m = f"{type(e.exception).__name__}: {e.exception}"
        parts.append(f"{i}\n{indent(m, ' ' * 4)}")
    return "\n".join(parts)
