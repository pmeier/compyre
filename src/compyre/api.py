from __future__ import annotations

import dataclasses
import functools
import inspect
from collections import deque
from typing import Any, Callable, Deque, TypeVar

__all__ = ["CompareError", "EqualFnResult", "Pair", "UnpackFnResult", "compare"]


@dataclasses.dataclass
class Pair:
    index: tuple[str | int, ...]
    actual: Any
    expected: Any


UnpackFnResult = list[Pair] | Exception | None
EqualFnResult = bool | Exception | None


@dataclasses.dataclass
class CompareError:
    index: tuple[str | int, ...]
    error: Exception


T = TypeVar("T")


def _bind_fn_kwargs(
    fn: Callable[..., T], kwargs: dict[str, Any]
) -> tuple[Callable[[Pair], T], set[str]]:
    params = list(inspect.signature(fn, follow_wrapped=True).parameters.values())

    if not params:
        raise TypeError

    pair_arg, *params = params
    if pair_arg.kind not in {
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    }:
        raise TypeError

    bind_kwargs: dict[str, Any] = {}
    for p in params:
        if p.kind not in {
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }:
            raise TypeError

        v = kwargs.get(p.name, inspect.Parameter.empty)
        if v is not inspect.Parameter.empty:
            bind_kwargs[p.name] = v
        elif p.default is inspect.Parameter.empty:
            raise TypeError

    return functools.partial(fn, **bind_kwargs), set(bind_kwargs.keys())


def _parametrize_fns(
    unparametrized_fns: list[Callable[..., T]], kwargs: dict[str, Any]
) -> tuple[list[Callable[[Pair], T]], set[str]]:
    parametrized_fns: list[Callable[[Pair], T]] = []
    used_kwargs: set[str] = set()
    for ufn in unparametrized_fns:
        pfn, uks = _bind_fn_kwargs(ufn, kwargs)
        parametrized_fns.append(pfn)
        used_kwargs.update(uks)
    return parametrized_fns, used_kwargs


def compare(
    actual: Any,
    expected: Any,
    *,
    unpack_fns: list[Callable[..., UnpackFnResult]],
    equal_fns: list[Callable[..., EqualFnResult]],
    **kwargs: Any,
) -> list[CompareError]:
    parametrized_unpack_fns, used_unpack_kwargs = _parametrize_fns(unpack_fns, kwargs)
    parametrized_equal_fns, used_equal_kwargs = _parametrize_fns(equal_fns, kwargs)

    extra = set(kwargs.keys()) - (used_unpack_kwargs | used_equal_kwargs)
    if extra:
        raise TypeError

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
                errors.append(CompareError(index=pair.index, error=unpack_result))
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
            equal_result = ValueError("pair couldn't be handled")
        elif not equal_result:
            equal_result = AssertionError(
                f"{pair.actual!r} is not equal to {pair.expected!r}"
            )

        if isinstance(equal_result, Exception):
            errors.append(CompareError(index=pair.index, error=equal_result))

    return errors


def is_equal(
    actual: Any,
    expected: Any,
    *,
    unpack_fns: list[Callable[..., UnpackFnResult]],
    equal_fns: list[Callable[..., EqualFnResult]],
    **kwargs: Any,
) -> bool:
    return not compare(
        actual, expected, unpack_fns=unpack_fns, equal_fns=equal_fns, **kwargs
    )


def assert_equal(
    actual: Any,
    expected: Any,
    *,
    unpack_fns: list[Callable[..., UnpackFnResult]],
    equal_fns: list[Callable[..., EqualFnResult]],
    **kwargs: Any,
) -> None:
    errors = compare(
        actual, expected, unpack_fns=unpack_fns, equal_fns=equal_fns, **kwargs
    )
    if not errors:
        return None

    # FIXME
    raise AssertionError(str(errors))
