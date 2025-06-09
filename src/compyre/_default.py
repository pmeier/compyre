from collections.abc import Mapping
from typing import Any, Callable

from . import api, builtin
from ._availability import is_available
from .alias import Alias

__all__ = [
    "assert_equal",
    "default_equal_fns",
    "default_unpack_fns",
    "is_equal",
]

_DEFAULT_UNPACK_FNS: list[Callable[..., api.UnpackFnResult]] | None = None


def default_unpack_fns() -> list[Callable[..., api.UnpackFnResult]]:
    """Return a list of available builtin unpacking functions.

    Returns:
        The following unpacking functions in order if their requirements are met

            - [compyre.builtin.unpack_fns.pydantic_model][]
            - [compyre.builtin.unpack_fns.dataclasses_dataclass][]
            - [compyre.builtin.unpack_fns.collections_ordered_dict][]
            - [compyre.builtin.unpack_fns.collections_mapping][]
            - [compyre.builtin.unpack_fns.collections_sequence][]

    """
    global _DEFAULT_UNPACK_FNS
    if _DEFAULT_UNPACK_FNS is None:
        _DEFAULT_UNPACK_FNS = [
            fn
            for fn in [
                builtin.unpack_fns.pydantic_model,
                builtin.unpack_fns.dataclasses_dataclass,
                builtin.unpack_fns.collections_ordered_dict,
                builtin.unpack_fns.collections_mapping,
                builtin.unpack_fns.collections_sequence,
            ]
            if is_available(fn)
        ]

    return _DEFAULT_UNPACK_FNS.copy()


_DEFAULT_EQUAL_FNS: list[Callable[..., api.EqualFnResult]] | None = None


def default_equal_fns() -> list[Callable[..., api.EqualFnResult]]:
    """Return a list of available builtin equality check functions.

    Returns:
        The following unpacking functions in order if their requirements are met

            - [compyre.builtin.equal_fns.numpy_ndarray][]
            - [compyre.builtin.equal_fns.pandas_dataframe][]
            - [compyre.builtin.equal_fns.pandas_series][]
            - [compyre.builtin.equal_fns.torch_tensor][]
            - [compyre.builtin.equal_fns.builtins_number][]
            - [compyre.builtin.equal_fns.builtins_object][]

    """
    global _DEFAULT_EQUAL_FNS
    if _DEFAULT_EQUAL_FNS is None:
        _DEFAULT_EQUAL_FNS = [
            fn
            for fn in [
                builtin.equal_fns.numpy_ndarray,
                builtin.equal_fns.pandas_dataframe,
                builtin.equal_fns.pandas_series,
                builtin.equal_fns.torch_tensor,
                builtin.equal_fns.builtins_number,
                builtin.equal_fns.builtins_object,
            ]
            if is_available(fn)
        ]

    return _DEFAULT_EQUAL_FNS.copy()


def is_equal(
    actual: Any,
    expected: Any,
    aliases: Mapping[Alias, Any] | None = None,
    **kwargs: Any,
) -> bool:
    """Boolean equality check of the inputs.

    !!! info

        This function is a thin wrapper around [compyre.api.is_equal][] using [compyre.default_unpack_fns][] and
        [compyre.default_equal_fns][]. See [compyre.api.is_equal][] for a description of the remaining arguments.

    Returns:
        Whether the inputs are equal.

    """
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
    """Equality assertion of the inputs.

    !!! info

        This function is a thin wrapper around [compyre.api.assert_equal][] using [compyre.default_unpack_fns][] and
        [compyre.default_equal_fns][]. See [compyre.api.assert_equal][] for a description of the remaining arguments.

    Raises:
        AssertionError: If any input pair is not equal.

    """
    return api.assert_equal(
        actual,
        expected,
        unpack_fns=default_unpack_fns(),
        equal_fns=default_equal_fns(),
        aliases=aliases,
        **kwargs,
    )
