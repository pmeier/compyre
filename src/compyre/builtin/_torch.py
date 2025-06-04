from typing import Annotated

from compyre import alias, api
from compyre._availability import available_if

from ._utils import both_isinstance


@available_if("torch")
def torch_tensor(
    p: api.Pair,
    /,
    *,
    rtol: Annotated[float | None, alias.RELATIVE_TOLERANCE] = None,
    atol: Annotated[float | None, alias.ABSOLUTE_TOLERANCE] = None,
    equal_nan: Annotated[bool, alias.NAN_EQUALITY] = False,
) -> api.EqualFnResult:
    import torch

    if not both_isinstance(p, torch.Tensor):
        return None

    try:
        torch.testing.assert_close(
            p.actual,
            p.expected,
            rtol=rtol,
            atol=atol,
            equal_nan=equal_nan,
        )
        return True
    except AssertionError as result:
        return result
