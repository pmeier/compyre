from collections.abc import Mapping
from typing import Any, Callable

from . import api, builtin
from ._availability import is_available
from .alias import Alias

__all__ = [
    "assert_equal",
    "compare",
    "default_equal_fns",
    "default_unpack_fns",
    "is_equal",
]

_DEFAULT_UNPACK_FNS: list[Callable[..., api.UnpackFnResult]] | None = None


def default_unpack_fns() -> list[Callable[..., api.UnpackFnResult]]:
    global _DEFAULT_UNPACK_FNS
    if _DEFAULT_UNPACK_FNS is None:
        _DEFAULT_UNPACK_FNS = [
            fn
            for name in builtin.unpack_fns.__all__
            if is_available((fn := getattr(builtin.unpack_fns, name)))
        ]

    return _DEFAULT_UNPACK_FNS.copy()


_DEFAULT_EQUAL_FNS: list[Callable[..., api.EqualFnResult]] | None = None


def default_equal_fns() -> list[Callable[..., api.EqualFnResult]]:
    global _DEFAULT_EQUAL_FNS
    if _DEFAULT_EQUAL_FNS is None:
        _DEFAULT_EQUAL_FNS = [
            fn
            for name in builtin.equal_fns.__all__
            if is_available((fn := getattr(builtin.equal_fns, name)))
        ]

    return _DEFAULT_EQUAL_FNS.copy()


def compare(
    actual: Any,
    expected: Any,
    aliases: Mapping[Alias, Any] | None = None,
    **kwargs: Any,
) -> list[api.CompareError]:
    return api.compare(
        actual,
        expected,
        unpack_fns=default_unpack_fns(),
        equal_fns=default_equal_fns(),
        aliases=aliases,
        **kwargs,
    )


def is_equal(
    actual: Any,
    expected: Any,
    aliases: Mapping[Alias, Any] | None = None,
    **kwargs: Any,
) -> bool:
    return api.is_equal(
        actual,
        expected,
        unpack_fns=default_unpack_fns(),
        equal_fns=default_equal_fns(),
        aliases=aliases,
        **kwargs,
    )


def assert_equal(
    actual: Any,
    expected: Any,
    aliases: Mapping[Alias, Any] | None = None,
    **kwargs: Any,
) -> None:
    return api.assert_equal(
        actual,
        expected,
        unpack_fns=default_unpack_fns(),
        equal_fns=default_equal_fns(),
        aliases=aliases,
        **kwargs,
    )
