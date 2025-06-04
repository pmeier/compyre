from collections import OrderedDict

import pytest

from compyre import alias, api, builtin


class TestCollectionsMapping:
    @pytest.mark.parametrize(
        ("actual", "expected"), [(object(), object()), ({}, object()), (object(), {})]
    )
    def test_not_supported(self, actual, expected):
        assert (
            builtin.unpack_fns.collections_mapping(
                api.Pair(index=(), actual=actual, expected=expected)
            )
            is None
        )

    def test_pairs(self):
        def getitem(obj, index):
            for i in index:
                obj = obj[i]
            return obj

        actual = {"foo": "afoo", "bar": [0, 1, 2], "nested": {"baz": True}}
        expected = {"nested": {"baz": False}, "bar": [0, -1, -2], "foo": "efoo"}

        pairs = builtin.unpack_fns.collections_mapping(
            api.Pair(index=(), actual=actual, expected=expected)
        )

        assert len(pairs) == len(actual)
        for p in pairs:
            assert p.actual == getitem(actual, p.index)
            assert p.expected == getitem(expected, p.index)

    def test_keys_mismatch(self):
        actual = {"foo": "foo", "bar": "bar"}
        expected = {"foo": "foo", "baz": "baz"}

        result = builtin.unpack_fns.collections_mapping(
            api.Pair(index=(), actual=actual, expected=expected)
        )
        assert isinstance(result, Exception)
        assert all(
            s in str(result)
            for s in ["mapping keys mismatch", repr("bar"), repr("baz")]
        )


class TestCollectionsSequence:
    @pytest.mark.parametrize(
        ("actual", "expected"),
        [(object(), object()), ([], object()), (object(), []), ({}, {})],
    )
    def test_not_supported(self, actual, expected):
        assert (
            builtin.unpack_fns.collections_sequence(
                api.Pair(index=(), actual=actual, expected=expected)
            )
            is None
        )

    def test_pairs(self):
        index = ("index",)
        actual = ["foo", 0, [True]]
        expected = ["bar", 1, [False]]

        pairs = builtin.unpack_fns.collections_sequence(
            api.Pair(index=index, actual=actual, expected=expected)
        )

        assert len(pairs) == len(actual)
        assert [p.index for p in pairs] == [(*index, i) for i in range(len(actual))]
        assert [p.actual for p in pairs] == actual
        assert [p.expected for p in pairs] == expected

    def test_len_mismatch(self):
        actual = ["foo", "bar"]
        expected = ["baz"]

        result = builtin.unpack_fns.collections_sequence(
            api.Pair(index=(), actual=actual, expected=expected)
        )
        assert isinstance(result, Exception)
        assert all(
            s in str(result)
            for s in ["sequence length mismatch", str(len(actual)), str(len(expected))]
        )


class TestCollectionsOrderedDict:
    @pytest.mark.parametrize(
        ("actual", "expected"),
        [(object(), OrderedDict()), (OrderedDict(), object()), (OrderedDict(), {})],
    )
    def test_not_supported(self, actual, expected):
        assert (
            builtin.unpack_fns.collections_ordered_dict(
                api.Pair(index=(), actual=actual, expected=expected)
            )
            is None
        )

    def test_pairs(self):
        index = ("index",)
        actual = OrderedDict(
            [("foo", "afoo"), ("bar", [0, 1, 2]), ("nested", {"baz": True})]
        )
        expected = OrderedDict(
            [("foo", "efoo"), ("bar", [0, -1, -2]), ("nested", {"baz": False})]
        )

        pairs = builtin.unpack_fns.collections_ordered_dict(
            api.Pair(index=index, actual=actual, expected=expected)
        )

        assert len(pairs) == len(actual)
        assert [p.index for p in pairs] == [(*index, k) for k in actual.keys()]
        assert [p.actual for p in pairs] == list(actual.values())
        assert [p.expected for p in pairs] == list(expected.values())

    def test_keys_mismatch(self):
        actual = OrderedDict({"foo": "foo", "bar": "bar"})
        expected = OrderedDict({"foo": "foo", "baz": "baz"})

        result = builtin.unpack_fns.collections_ordered_dict(
            api.Pair(index=(), actual=actual, expected=expected)
        )
        assert isinstance(result, Exception)
        assert "ordered keys mismatch" in str(result)

    def test_keys_order_mismatch(self):
        actual = OrderedDict([("foo", "foo"), ("bar", "bar")])
        expected = OrderedDict([("bar", "bar"), ("foo", "foo")])

        result = builtin.unpack_fns.collections_ordered_dict(
            api.Pair(index=(), actual=actual, expected=expected)
        )
        assert isinstance(result, Exception)
        assert "ordered keys mismatch" in str(result)


class TestBuiltinsIntFloat:
    @pytest.mark.parametrize(
        ("actual", "expected"),
        [(object(), object()), (1.0, object()), (object(), 2), (False, 0), (1.0, True)],
    )
    def test_not_supported(self, actual, expected):
        assert (
            builtin.unpack_fns.collections_sequence(
                api.Pair(index=(), actual=actual, expected=expected)
            )
            is None
        )

    @pytest.mark.parametrize("expected_type", [int, float])
    def test_rtol_equal(self, expected_type):
        rel_tol = 1e-2
        expected = expected_type(1.0)
        actual = expected * (1 + rel_tol / 2)

        result = builtin.equal_fns.builtins_int_float(
            api.Pair(index=(), actual=actual, expected=expected),
            rel_tol=rel_tol,
            abs_tol=0,
        )
        assert result is True

    @pytest.mark.parametrize("expected_type", [int, float])
    def test_rtol_not_equal(self, expected_type):
        rel_tol = 1e-2
        expected = expected_type(1.0)
        actual = expected * (1 + rel_tol * 2)

        result = builtin.equal_fns.builtins_int_float(
            api.Pair(index=(), actual=actual, expected=expected),
            rel_tol=rel_tol,
            abs_tol=0,
        )
        assert isinstance(result, AssertionError)

    @pytest.mark.parametrize("expected_type", [int, float])
    def test_rtol_alias(self, expected_type):
        rtol = 1e-2
        expected = expected_type(1.0)
        actual = expected * (1 + rtol / 2)

        api.assert_equal(
            actual,
            expected,
            unpack_fns=[],
            equal_fns=[builtin.equal_fns.builtins_int_float],
            aliases={alias.RELATIVE_TOLERANCE: rtol},
            abs_tol=0,
        )

    @pytest.mark.parametrize("expected_type", [int, float])
    def test_atol_equal(self, expected_type):
        abs_tol = 1e-2
        expected = expected_type(1.0)
        actual = expected + abs_tol / 2

        result = builtin.equal_fns.builtins_int_float(
            api.Pair(index=(), actual=actual, expected=expected),
            abs_tol=abs_tol,
            rel_tol=0,
        )
        assert result is True

    @pytest.mark.parametrize("expected_type", [int, float])
    def test_atol_not_equal(self, expected_type):
        abs_tol = 1e-2
        expected = expected_type(1.0)
        actual = expected + abs_tol * 2

        result = builtin.equal_fns.builtins_int_float(
            api.Pair(index=(), actual=actual, expected=expected),
            abs_tol=abs_tol,
            rel_tol=0,
        )
        assert isinstance(result, AssertionError)

    @pytest.mark.parametrize("expected_type", [int, float])
    def test_atol_alias(self, expected_type):
        abs_tol = 1e-2
        expected = expected_type(1.0)
        actual = expected + abs_tol / 2

        api.assert_equal(
            actual,
            expected,
            unpack_fns=[],
            equal_fns=[builtin.equal_fns.builtins_int_float],
            aliases={alias.ABSOLUTE_TOLERANCE: abs_tol},
            rel_tol=0,
        )


class TestStdlibObject:
    pass
