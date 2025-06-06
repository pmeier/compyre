import numpy as np
import pandas as pd
import pytest

from compyre import alias, api, builtin


class TestPandasSeries:
    @pytest.mark.parametrize(
        ("actual", "expected"),
        [
            (object(), pd.Series()),
            (pd.Series(), object()),
            (pd.Series(), []),
            (pd.Series(), np.array([])),
        ],
    )
    def test_not_supported(self, actual, expected):
        assert (
            builtin.equal_fns.pandas_series(
                api.Pair(index=(), actual=actual, expected=expected)
            )
            is None
        )

    def test_equal(self):
        value = pd.Series([1.0], dtype=np.float64)

        result = builtin.equal_fns.pandas_series(
            api.Pair(index=(), actual=value.copy(), expected=value.copy())
        )
        assert result is True

    def test_rtol_equal(self):
        rtol = 1e-2
        expected = pd.Series([1.0], dtype=np.float64)
        actual = expected * (1 + rtol / 2)

        result = builtin.equal_fns.pandas_series(
            api.Pair(index=(), actual=actual, expected=expected),
            rtol=rtol,
            atol=0,
        )
        assert result is True

    def test_rtol_not_equal(self):
        rtol = 1e-2
        expected = pd.Series([1.0], dtype=np.float64)
        actual = expected * (1 + rtol * 2)

        result = builtin.equal_fns.pandas_series(
            api.Pair(index=(), actual=actual, expected=expected),
            rtol=rtol,
            atol=0,
        )
        assert isinstance(result, AssertionError)

    def test_rtol_alias(self):
        rtol = 1e-2
        expected = pd.Series([1.0], dtype=np.float64)
        actual = expected * (1 + rtol / 2)

        api.assert_equal(
            actual,
            expected,
            unpack_fns=[],
            equal_fns=[builtin.equal_fns.pandas_series],
            aliases={alias.RELATIVE_TOLERANCE: rtol},
            atol=0,
        )

    def test_atol_equal(self):
        atol = 1e-2
        expected = pd.Series([1.0], dtype=np.float64)
        actual = expected + atol / 2

        result = builtin.equal_fns.pandas_series(
            api.Pair(index=(), actual=actual, expected=expected),
            atol=atol,
            rtol=0,
        )
        assert result is True

    def test_atol_not_equal(self):
        atol = 1e-2
        expected = pd.Series([1.0], dtype=np.float64)
        actual = expected + atol * 2

        result = builtin.equal_fns.pandas_series(
            api.Pair(index=(), actual=actual, expected=expected),
            atol=atol,
            rtol=0,
        )
        assert isinstance(result, AssertionError)

    def test_atol_alias(self):
        atol = 1e-2
        expected = pd.Series([1.0], dtype=np.float64)
        actual = expected + atol / 2

        api.assert_equal(
            actual,
            expected,
            unpack_fns=[],
            equal_fns=[builtin.equal_fns.pandas_series],
            aliases={alias.ABSOLUTE_TOLERANCE: atol},
            rtol=0,
        )


class TestPandasDataframe:
    @pytest.mark.parametrize(
        ("actual", "expected"),
        [
            (object(), pd.DataFrame()),
            (pd.DataFrame(), object()),
        ],
    )
    def test_not_supported(self, actual, expected):
        assert (
            builtin.equal_fns.pandas_dataframe(
                api.Pair(index=(), actual=actual, expected=expected)
            )
            is None
        )

    def test_equal(self):
        value = pd.DataFrame([1.0], dtype=np.float64)

        result = builtin.equal_fns.pandas_series(
            api.Pair(index=(), actual=value.copy(), expected=value.copy())
        )
        assert result is True

    def test_rtol_equal(self):
        rtol = 1e-2
        expected = pd.DataFrame([1.0], dtype=np.float64)
        actual = expected * (1 + rtol / 2)

        result = builtin.equal_fns.pandas_dataframe(
            api.Pair(index=(), actual=actual, expected=expected),
            rtol=rtol,
            atol=0,
        )
        assert result is True

    def test_rtol_not_equal(self):
        rtol = 1e-2
        expected = pd.DataFrame([1.0], dtype=np.float64)
        actual = expected * (1 + rtol * 2)

        result = builtin.equal_fns.pandas_dataframe(
            api.Pair(index=(), actual=actual, expected=expected),
            rtol=rtol,
            atol=0,
        )
        assert isinstance(result, AssertionError)

    def test_rtol_alias(self):
        rtol = 1e-2
        expected = pd.DataFrame([1.0], dtype=np.float64)
        actual = expected * (1 + rtol / 2)

        api.assert_equal(
            actual,
            expected,
            unpack_fns=[],
            equal_fns=[builtin.equal_fns.pandas_dataframe],
            aliases={alias.RELATIVE_TOLERANCE: rtol},
            atol=0,
        )

    def test_atol_equal(self):
        atol = 1e-2
        expected = pd.DataFrame([1.0], dtype=np.float64)
        actual = expected + atol / 2

        result = builtin.equal_fns.pandas_dataframe(
            api.Pair(index=(), actual=actual, expected=expected),
            atol=atol,
            rtol=0,
        )
        assert result is True

    def test_atol_not_equal(self):
        atol = 1e-2
        expected = pd.DataFrame([1.0], dtype=np.float64)
        actual = expected + atol * 2

        result = builtin.equal_fns.pandas_dataframe(
            api.Pair(index=(), actual=actual, expected=expected),
            atol=atol,
            rtol=0,
        )
        assert isinstance(result, AssertionError)

    def test_atol_alias(self):
        atol = 1e-2
        expected = pd.DataFrame([1.0], dtype=np.float64)
        actual = expected + atol / 2

        api.assert_equal(
            actual,
            expected,
            unpack_fns=[],
            equal_fns=[builtin.equal_fns.pandas_dataframe],
            aliases={alias.ABSOLUTE_TOLERANCE: atol},
            rtol=0,
        )
