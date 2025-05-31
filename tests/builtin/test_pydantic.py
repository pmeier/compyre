import pydantic
import pytest

from compyre import api, builtin


class EmptyModel(pydantic.BaseModel):
    pass


class SimpleModel(pydantic.BaseModel):
    foo: str
    bar: list[int]


class NestedModel(pydantic.BaseModel):
    simple_model: SimpleModel
    baz: bool


class UndumpableModel(pydantic.BaseModel):
    @pydantic.model_serializer()
    def fail(self):
        raise ValueError()


class TestPydanticModel:
    @pytest.mark.parametrize(
        ("actual", "expected"),
        [(object(), object()), (EmptyModel(), object()), (object(), EmptyModel())],
    )
    def test_not_supported(self, actual, expected):
        assert (
            builtin.unpack_fns.pydantic_model(
                api.Pair(index=(), actual=actual, expected=expected)
            )
            is None
        )

    def test_pairs(self):
        index = ("index",)
        model = NestedModel(
            simple_model=SimpleModel(foo="foo", bar=[0, 1, 2]), baz=True
        )

        pairs = builtin.unpack_fns.pydantic_model(
            api.Pair(
                index=index,
                actual=model.model_copy(deep=True),
                expected=model.model_copy(deep=True),
            )
        )

        assert len(pairs) == 1
        pair = pairs[0]

        assert pair.index == index

        model_dumped = model.model_dump(mode="python")
        assert pair.actual == model_dumped
        assert pair.expected == model_dumped

    @pytest.mark.parametrize(
        ("actual", "expected"),
        [(EmptyModel(), UndumpableModel()), (UndumpableModel(), EmptyModel())],
    )
    def test_model_dump_exception(self, actual, expected):
        result = builtin.unpack_fns.pydantic_model(
            api.Pair(index=(), actual=actual, expected=expected)
        )
        assert isinstance(result, Exception)
