from typing import Any

from . import api, builtin
from ._availability import is_available

__all__ = [
    "assert_equal",
    "compare",
    "default_equal_fns",
    "default_unpack_fns",
    "is_equal",
]

_DEFAULT_UNPACK_FNS: list | None = None


def default_unpack_fns() -> list:
    global _DEFAULT_UNPACK_FNS
    if _DEFAULT_UNPACK_FNS is None:
        _DEFAULT_UNPACK_FNS = [
            fn
            for fn in [
                builtin.unpack_fns.pydantic_model,
                builtin.unpack_fns.stdlib_mapping,
                builtin.unpack_fns.stdlib_sequence,
            ]
            if is_available(fn)
        ]

    return _DEFAULT_UNPACK_FNS.copy()


_DEFAULT_EQUAL_FNS: list | None = None


def default_equal_fns() -> list:
    global _DEFAULT_EQUAL_FNS
    if _DEFAULT_EQUAL_FNS is None:
        _DEFAULT_EQUAL_FNS = [
            fn
            for fn in [
                builtin.equal_fns.stdlib_number,
                builtin.equal_fns.stdlib_object,
            ]
            if is_available(fn)
        ]

    return _DEFAULT_EQUAL_FNS.copy()


def compare(actual: Any, expected: Any, **kwargs: Any) -> list[api.CompareError]:
    return api.compare(
        actual,
        expected,
        unpack_fns=default_unpack_fns(),
        equal_fns=default_equal_fns(),
        **kwargs,
    )


def is_equal(actual: Any, expected: Any, **kwargs: Any) -> bool:
    return api.is_equal(
        actual,
        expected,
        unpack_fns=default_unpack_fns(),
        equal_fns=default_equal_fns(),
        **kwargs,
    )


def assert_equal(actual: Any, expected: Any, **kwargs: Any) -> None:
    return api.assert_equal(
        actual,
        expected,
        unpack_fns=default_unpack_fns(),
        equal_fns=default_equal_fns(),
        **kwargs,
    )
