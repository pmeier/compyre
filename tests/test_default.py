from copy import deepcopy

import numpy as np
import pydantic
import pytest
import torch

import compyre


def test_default_unpack_fns():
    assert set(compyre.default_unpack_fns()) == {
        getattr(compyre.builtin.unpack_fns, n)
        for n in compyre.builtin.unpack_fns.__all__
    }


def test_default_equal_fns():
    assert set(compyre.default_equal_fns()) == {
        getattr(compyre.builtin.equal_fns, n) for n in compyre.builtin.equal_fns.__all__
    }


class SimpleModel(pydantic.BaseModel):
    foo: str
    bar: list[int]


class NestedModel(pydantic.BaseModel):
    simple_model: SimpleModel
    baz: bool


@pytest.fixture
def value():
    return {
        "stdlib": [
            {"mapping": True},
            ["s", "e", "q"],
            None,
            True,
            False,
            "abc",
            1,
            2.0,
            3.0j,
        ],
        "pydantic": [
            NestedModel(
                simple_model=SimpleModel(foo="foofoo", bar=[0, 1, 42]), baz=True
            ),
        ],
        "numpy": [
            np.array([0.0, 1.0, np.pi]),
        ],
        "torch": [torch.tensor([-1, 314])],
    }


def test_is_equal(value):
    assert compyre.is_equal(deepcopy(value), deepcopy(value))


def test_assert_equal(value):
    compyre.assert_equal(deepcopy(value), deepcopy(value))
