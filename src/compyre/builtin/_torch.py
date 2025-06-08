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
    """Checks equality for [torch.Tensor][]s using [torch.testing.assert_close][].

    Args:
        p: Pair to be compared.
        rtol: Relative tolerance. If specified `atol` must also be specified. If omitted, default values based on the
              `dtype` are selected. See [torch.testing.assert_close][] for details. Can also be set through
              [compyre.alias.RELATIVE_TOLERANCE][].
        atol: Absolute tolerance. If specified `rtol` must also be specified. If omitted, default values based on the
              [`dtype`][torch.dtype] are selected. See [torch.testing.assert_close][] for details. Can also be set
              through [compyre.alias.ABSOLUTE_TOLERANCE][].
        equal_nan: Whether two `NaN` values are considered equal. Can also be set through
              [compyre.alias.NAN_EQUALITY][].

    Returns:
       (None): If [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are not [torch.Tensor][]s.
       (True): If [torch.testing.assert_close][] returns without error for the input pair.
       (AssertionError): Any [AssertionError][] raised by [torch.testing.assert_close][] for the input pair.

    Raises:
        RuntimeError: If [torch][] is not available.
    """
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
