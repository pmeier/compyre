from __future__ import annotations

import dataclasses
import functools
import inspect
import typing
from collections import deque
from collections.abc import Mapping, Sequence
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
    index: tuple[str | int, ...]
    actual: Any
    expected: Any


UnpackFnResult = Sequence[Pair] | Exception | None
EqualFnResult = bool | Exception | None


@dataclasses.dataclass
class CompareError:
    index: tuple[str | int, ...]
    exception: Exception


def compare(
    actual: Any,
    expected: Any,
    *,
    unpack_fns: Sequence[Callable[..., UnpackFnResult]],
    equal_fns: Sequence[Callable[..., EqualFnResult]],
    aliases: Mapping[Alias, Any] | None = None,
    **kwargs: Any,
) -> list[CompareError]:
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
            equal_result = ValueError(
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

    extra = (kwargs.keys() | aliases.keys()) - bound
    if extra:
        raise TypeError(
            f"unexpected keyword argument(s) {', '.join(repr(e) for e in sorted(extra))}"
        )

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
    return not compare(
        actual,
        expected,
        unpack_fns=unpack_fns,
        equal_fns=equal_fns,
        aliases=aliases,
        **kwargs,
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
    errors = compare(
        actual,
        expected,
        unpack_fns=unpack_fns,
        equal_fns=equal_fns,
        aliases=aliases,
        **kwargs,
    )
    if not errors:
        return None

    # FIXME
    raise AssertionError(str(errors))
