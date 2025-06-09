from typing import Annotated

from compyre import alias, api
from compyre._availability import available_if

from ._utils import both_isinstance


@available_if("numpy")
def numpy_ndarray(
    p: api.Pair,
    /,
    *,
    rtol: Annotated[float, alias.RELATIVE_TOLERANCE] = 1e-7,
    atol: Annotated[float, alias.ABSOLUTE_TOLERANCE] = 0.0,
    equal_nan: Annotated[bool, alias.NAN_EQUALITY] = True,
    verbose: bool = True,
) -> api.EqualFnResult:
    """Check equality for [numpy.ndarray][]s using [numpy.testing.assert_allclose][].

    Args:
        p: Pair to be compared.
        rtol: Relative tolerance. See [numpy.testing.assert_allclose][] for details. Can also be set through
              [compyre.alias.RELATIVE_TOLERANCE][].
        atol: Absolute tolerance. See [numpy.testing.assert_allclose][] for details. Can also be set
              through [compyre.alias.ABSOLUTE_TOLERANCE][].
        equal_nan: Whether two `NaN` values are considered equal. Can also be set through
              [compyre.alias.NAN_EQUALITY][].
        verbose: Whether mismatching values are included in the error message.

    Returns:
       (None): If [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are not [numpy.ndarray][]s.
       (True): If [numpy.testing.assert_allclose][] returns without error for the input pair.
       (AssertionError): Any [AssertionError][] raised by [numpy.testing.assert_allclose][] for the input pair.

    Raises:
        RuntimeError: If [numpy][] is not available.

    """
    import numpy as np

    if not both_isinstance(p, np.ndarray):
        return None

    try:
        np.testing.assert_allclose(
            p.actual,
            p.expected,
            rtol=rtol,
            atol=atol,
            equal_nan=equal_nan,
            verbose=verbose,
        )
        return True
    except AssertionError as result:
        return result
