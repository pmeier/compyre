import inspect
from copy import deepcopy

import pytest

from compyre import api, builtin


class TestBindKwargs:
    def test_no_params(self):
        def no_params():  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._bind_kwargs(no_params, {})

    def test_pair_arg_keyword_only(self):
        def pair_arg_keyword_only(*, pair):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._bind_kwargs(pair_arg_keyword_only, {})

    def test_pair_arg_var_positional(self):
        def pair_arg_var_positional(*args):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._bind_kwargs(pair_arg_var_positional, {})

    def test_pair_arg_var_keyword(self):
        def pair_arg_var_keyword(**kwargs):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._bind_kwargs(pair_arg_var_keyword, {})

    def test_param_positional_only(self):
        def param_positional_only(pair, param, /):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._bind_kwargs(param_positional_only, {"param": True})

    def test_param_var_positional(self):
        def param_var_positional(pair, *params):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._bind_kwargs(param_var_positional, {"params": True})

    def test_param_var_keyword(self):
        def param_var_keyword(pair, param, **params):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._bind_kwargs(param_var_keyword, {"param": True})

    def test_missing_required(self):
        def required_param(pair, param):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._bind_kwargs(required_param, {})

    def test_bind(self):
        def fn(pair, /, *, foo, bar="bar", baz="baz"):  # pragma: no cover
            pass

        bound_fn, used_kwargs = api._bind_kwargs(
            fn, {"foo": "foo", "bar": "barbar", "unused": True}
        )

        params = inspect.signature(bound_fn).parameters
        assert params["foo"].default == "foo"
        assert params["bar"].default == "barbar"
        assert params["baz"].default == "baz"

        assert {"foo", "bar"} == used_kwargs


class TestCompare:
    def test_unused_kwargs(self):
        def unpack_fn(pair, /, *, foo):  # pragma: no cover
            pass

        def equal_fn(pair, /, *, bar):  # pragma: no cover
            pass

        with pytest.raises(TypeError):
            api.compare(
                None,
                None,
                unpack_fns=[unpack_fn],
                equal_fns=[equal_fn],
                foo="foo",
                bar="bar",
                baz="baz",
            )

    def test_unpack_fn_exception(self):
        exc = Exception()

        def unpack_fn(pair, /):
            return exc

        errors = api.compare(
            None,
            None,
            unpack_fns=[unpack_fn],
            equal_fns=[builtin.equal_fns.builtins_object],
        )

        assert len(errors) == 1
        error = errors[0]

        assert error.index == ()
        assert error.exception is exc

    def test_unpack_pairs_order(self):
        values = [0, 1, {"foo": "bar", "baz": True}, [2, 3]]
        expected = [0, 1, "bar", True, 2, 3]

        actual = []

        def equal_fn(pair, /):
            assert pair.actual == pair.expected
            nonlocal actual
            actual.append(pair.actual)
            return True

        errors = api.compare(
            deepcopy(values),
            deepcopy(values),
            unpack_fns=[
                builtin.unpack_fns.collections_mapping,
                builtin.unpack_fns.collections_sequence,
            ],
            equal_fns=[equal_fn],
        )

        assert not errors
        assert actual == expected

    def test_unhandled(self):
        def unpack_fn(pair, /):
            return None

        def equal_fn(pair, /):
            return None

        errors = api.compare(None, None, unpack_fns=[unpack_fn], equal_fns=[equal_fn])

        assert len(errors) == 1
        error = errors[0]

        assert error.index == ()

        assert isinstance(error.exception, ValueError)
        assert "couldn't be handled" in str(error.exception)

    def test_default_error_message(self):
        class Object:
            def __str__(self):  # pragma: no cover
                return f"str({id(self)})"

            def __repr__(self):
                return f"repr({id(self)})"

        actual = Object()
        expected = Object()

        def equal_fn(pair, /):
            return False

        errors = api.compare(actual, expected, unpack_fns=[], equal_fns=[equal_fn])

        assert len(errors) == 1
        error = errors[0]

        assert error.index == ()

        assert isinstance(error.exception, AssertionError)
        assert repr(actual) in str(error.exception)
        assert repr(expected) in str(error.exception)


@pytest.mark.parametrize("result", [True, False])
def test_is_equal(result):
    def equal_fn(pair, /):
        return result

    assert api.is_equal(None, None, unpack_fns=[], equal_fns=[equal_fn]) is result


class TestAssertEqual:
    def test_no_errors(self):
        def equal_fn(pair, /):
            return True

        api.assert_equal(None, None, unpack_fns=[], equal_fns=[equal_fn])

    def test_errors(self):
        # FIXME
        pass
