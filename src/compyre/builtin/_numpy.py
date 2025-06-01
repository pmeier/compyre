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
    equal_nan: bool = True,
    verbose: bool = True,
) -> api.EqualFnResult:
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
