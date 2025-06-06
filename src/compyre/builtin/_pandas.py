from typing import Annotated

from compyre import alias, api
from compyre._availability import available_if

from ._utils import both_isinstance


@available_if("pandas")
def pandas_dataframe(
    p: api.Pair,
    /,
    *,
    rtol: Annotated[float | None, alias.RELATIVE_TOLERANCE] = None,
    atol: Annotated[float | None, alias.ABSOLUTE_TOLERANCE] = None,
) -> api.EqualFnResult:
    import pandas as pd

    if not both_isinstance(p, pd.DataFrame):
        return None

    try:
        pd.testing.assert_frame_equal(
            p.actual,
            p.expected,
            rtol=rtol,  # type: ignore[arg-type]
            atol=atol,  # type: ignore[arg-type]
        )
        return True
    except AssertionError as result:
        return result


@available_if("pandas")
def pandas_series(
    p: api.Pair,
    /,
    *,
    rtol: Annotated[float | None, alias.RELATIVE_TOLERANCE] = None,
    atol: Annotated[float | None, alias.ABSOLUTE_TOLERANCE] = None,
) -> api.EqualFnResult:
    import pandas as pd

    if not both_isinstance(p, pd.Series):
        return None

    try:
        pd.testing.assert_series_equal(
            p.actual,
            p.expected,
            rtol=rtol,  # type: ignore[arg-type]
            atol=atol,  # type: ignore[arg-type]
        )
        return True
    except AssertionError as result:
        return result
