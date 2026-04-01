from compyre import api, utils
from compyre._availability import available_if

from ._stdlib import collections_mapping

__all__ = ["pydantic_model"]


@available_if("pydantic>=2,<3")
def pydantic_model(p: api.Pair, /) -> api.UnpackFnResult:
    """Unpack [pydantic.BaseModel][]s using [pydantic.BaseModel.model_dump][].

    Args:
        p: Pair to be unpacked.

    Returns:
        (None): If [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] are not
            [pydantic.BaseModel][]s.
        (list[api.Pair]): The [`actual`][compyre.api.Pair] and [`expected`][compyre.api.Pair] values of each pair are
            the corresponding values of the input models, while the [`index`][compyre.api.Pair] is `p.index` extended
            by the corresponding field name.
        (ValueError): If the fields of [`p.actual`][compyre.api.Pair] and [`p.expected`][compyre.api.Pair] mismatch.
        (Exception): Any [Exception][] raised by [pydantic.BaseModel.model_dump][] for the input pair.

    Raises:
        RuntimeError: If `pydantic >=2, <3` is not available.

    """
    import pydantic

    if not utils.both_isinstance(p, pydantic.BaseModel):
        return None

    try:
        actual = p.actual.model_dump()
        expected = p.expected.model_dump()
    except Exception as result:
        return result

    return collections_mapping(
        api.Pair(index=p.index, actual=actual, expected=expected)
    )
