from typing import Annotated

from compyre import alias, api
from compyre._availability import available_if

from ._utils import both_isinstance


@available_if("pandas")
def pandas_dataframe(
    p: api.Pair,
    /,
    *,
    rtol: Annotated[float, alias.RELATIVE_TOLERANCE] = 1e-5,
    atol: Annotated[float, alias.ABSOLUTE_TOLERANCE] = 1e-8,
) -> api.EqualFnResult:
    """Check equality for [pandas.DataFrame][]s using [pandas.testing.assert_frame_equal][].

    Args:
        p: Pair to be compared.
        rtol: Relative tolerance. See [pandas.testing.assert_frame_equal][] for details. Can also be set through
              [compyre.alias.RELATIVE_TOLERANCE][].
        atol: Absolute tolerance. See [pandas.testing.assert_frame_equal][] for details. Can also be set
              through [compyre.alias.ABSOLUTE_TOLERANCE][].

    Returns:
       (None): If [[`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are not [pandas.DataFrame][]s.
       (True): If [pandas.testing.assert_frame_equal][] returns without error for the input pair.
       (AssertionError): Any [AssertionError][] raised by [pandas.testing.assert_frame_equal][] for the input pair.

    Raises:
        RuntimeError: If [pandas][] is not available.

    """
    import pandas as pd

    if not both_isinstance(p, pd.DataFrame):
        return None

    try:
        pd.testing.assert_frame_equal(
            p.actual,
            p.expected,
            rtol=rtol,
            atol=atol,
        )
        return True
    except AssertionError as result:
        return result


@available_if("pandas")
def pandas_series(
    p: api.Pair,
    /,
    *,
    rtol: Annotated[float, alias.RELATIVE_TOLERANCE] = 1e-5,
    atol: Annotated[float, alias.ABSOLUTE_TOLERANCE] = 1e-8,
) -> api.EqualFnResult:
    """Check equality for [pandas.Series][]s using [pandas.testing.assert_series_equal][].

    Args:
        p: Pair to be compared.
        rtol: Relative tolerance. See [pandas.testing.assert_series_equal][] for details. Can also be set through
              [compyre.alias.RELATIVE_TOLERANCE][].
        atol: Absolute tolerance. See [pandas.testing.assert_series_equal][] for details. Can also be set
              through [compyre.alias.ABSOLUTE_TOLERANCE][].

    Returns:
       (None): If [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are not [pandas.Series][]s.
       (True): If [pandas.testing.assert_series_equal][] returns without error for the input pair.
       (AssertionError): Any [AssertionError][] raised by [pandas.testing.assert_series_equal][] for the input pair.

    Raises:
        RuntimeError: If [pandas][] is not available.

    """
    import pandas as pd

    if not both_isinstance(p, pd.Series):
        return None

    try:
        pd.testing.assert_series_equal(
            p.actual,
            p.expected,
            rtol=rtol,
            atol=atol,
        )
        return True
    except AssertionError as result:
        return result
