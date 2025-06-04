import contextlib

import numpy as np
import pytest
import torch

from compyre import alias, api, builtin


class TestTorchTensor:
    @pytest.mark.parametrize(
        ("actual", "expected"),
        [
            (object(), torch.tensor([])),
            (torch.tensor([]), object()),
            (torch.tensor([]), np.array([])),
        ],
    )
    def test_not_supported(self, actual, expected):
        assert (
            builtin.equal_fns.torch_tensor(
                api.Pair(index=(), actual=actual, expected=expected)
            )
            is None
        )

    def test_rtol_equal(self):
        rtol = 1e-2
        expected = torch.tensor([1.0], dtype=torch.float64)
        actual = expected * (1 + rtol / 2)

        result = builtin.equal_fns.torch_tensor(
            api.Pair(index=(), actual=actual, expected=expected),
            rtol=rtol,
            atol=0,
        )
        assert result is True

    def test_rtol_not_equal(self):
        rtol = 1e-2
        expected = torch.tensor([1.0], dtype=torch.float64)
        actual = expected * (1 + rtol * 2)

        result = builtin.equal_fns.torch_tensor(
            api.Pair(index=(), actual=actual, expected=expected),
            rtol=rtol,
            atol=0,
        )
        assert isinstance(result, AssertionError)

    def test_rtol_alias(self):
        rtol = 1e-2
        expected = torch.tensor([1.0], dtype=torch.float64)
        actual = expected * (1 + rtol / 2)

        api.assert_equal(
            actual,
            expected,
            unpack_fns=[],
            equal_fns=[builtin.equal_fns.torch_tensor],
            aliases={alias.RELATIVE_TOLERANCE: rtol},
            atol=0,
        )

    def test_atol_equal(self):
        atol = 1e-2
        expected = torch.tensor([1.0], dtype=torch.float64)
        actual = expected + atol / 2

        result = builtin.equal_fns.torch_tensor(
            api.Pair(index=(), actual=actual, expected=expected),
            atol=atol,
            rtol=0,
        )
        assert result is True

    def test_atol_not_equal(self):
        atol = 1e-2
        expected = torch.tensor([1.0], dtype=torch.float64)
        actual = expected + atol * 2

        result = builtin.equal_fns.torch_tensor(
            api.Pair(index=(), actual=actual, expected=expected),
            atol=atol,
            rtol=0,
        )
        assert isinstance(result, AssertionError)

    def test_atol_alias(self):
        atol = 1e-2
        expected = torch.tensor([1.0], dtype=torch.float64)
        actual = expected + atol / 2

        api.assert_equal(
            actual,
            expected,
            unpack_fns=[],
            equal_fns=[builtin.equal_fns.torch_tensor],
            aliases={alias.ABSOLUTE_TOLERANCE: atol},
            rtol=0,
        )

    @pytest.mark.parametrize("equal_nan", [True, False])
    def test_equal_nan(self, equal_nan):
        expected = torch.tensor([float("NaN")])
        actual = expected.clone()

        result = builtin.equal_fns.torch_tensor(
            api.Pair(index=(), actual=actual, expected=expected), equal_nan=equal_nan
        )

        if equal_nan:
            assert result is True
        else:
            assert isinstance(result, AssertionError)

    @pytest.mark.parametrize("equal_nan", [True, False])
    def test_equal_nan_alias(self, equal_nan):
        expected = torch.tensor([float("NaN")])
        actual = expected.clone()

        with contextlib.nullcontext() if equal_nan else pytest.raises(AssertionError):
            api.assert_equal(
                actual,
                expected,
                unpack_fns=[],
                equal_fns=[builtin.equal_fns.torch_tensor],
                aliases={alias.NAN_EQUALITY: equal_nan},
            )
