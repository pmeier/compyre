from compyre._availability import available_if
from compyre.api import Pair, UnpackFnResult

from ._stdlib import collections_mapping
from ._utils import both_isinstance

__all__ = ["pydantic_model"]


@available_if("pydantic>=2,<3")
def pydantic_model(p: Pair, /) -> UnpackFnResult:
    import pydantic

    if not both_isinstance(p, pydantic.BaseModel):
        return None

    try:
        actual = p.actual.model_dump(mode="python")
        expected = p.expected.model_dump(mode="python")
    except Exception as result:
        return result

    return collections_mapping(Pair(index=p.index, actual=actual, expected=expected))
