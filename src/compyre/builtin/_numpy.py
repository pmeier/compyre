from compyre._availability import available_if
from compyre.api import EqualFnResult, Pair

from ._utils import both_isinstance


@available_if("numpy")
def numpy_ndarray(
    p: Pair,
    /,
    *,
    rtol: float = 1e-7,
    atol: float = 0.0,
    equal_nan: bool = True,
    verbose: bool = True,
) -> EqualFnResult:
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
