from . import api, builtin
from ._default import (
    assert_equal,
    compare,
    default_equal_fns,
    default_unpack_fns,
    is_equal,
)

try:
    from ._version import __version__
except ModuleNotFoundError:
    import warnings

    warnings.warn("compyre was not properly installed!", stacklevel=2)
    del warnings

    __version__ = "UNKNOWN"

__all__ = [
    "__version__",
    "api",
    "assert_equal",
    "compare",
    "default_equal_fns",
    "default_unpack_fns",
    "is_equal",
]
