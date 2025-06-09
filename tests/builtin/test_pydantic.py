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
        simple_model = SimpleModel(foo="foo", bar=[0, 1, 2])
        model = NestedModel(simple_model=simple_model, baz=True)

        pairs = builtin.unpack_fns.pydantic_model(
            api.Pair(
                index=index,
                actual=model.model_copy(deep=True),
                expected=model.model_copy(deep=True),
            )
        )

        assert len(pairs) == 2

        pair = pairs[0]
        assert pair.index == (*index, "simple_model")
        assert pair.actual == pair.expected == simple_model.model_dump(mode="python")

        pair = pairs[1]
        assert pair.index == (*index, "baz")
        assert pair.actual == pair.expected == True  # noqa: E712

    @pytest.mark.parametrize(
        ("actual", "expected"),
        [(EmptyModel(), UndumpableModel()), (UndumpableModel(), EmptyModel())],
    )
    def test_model_dump_exception(self, actual, expected):
        result = builtin.unpack_fns.pydantic_model(
            api.Pair(index=(), actual=actual, expected=expected)
        )
        assert isinstance(result, Exception)
