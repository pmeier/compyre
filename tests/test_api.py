import inspect
from copy import deepcopy
from typing import Annotated, Any

import pytest

from compyre import alias, api, builtin


class TestParametrizeFns:
    def test_parametrize(self):
        baz_alias = alias.Alias("baz")

        def unpack_fn(pair, /, *, foo):  # pragma: no cover
            pass

        def equal_fn(
            pair, /, *, bar="bar", baz: Annotated[Any, baz_alias]
        ):  # pragma: no cover
            pass

        parametrized_unpack_fns, parametrized_equal_fns = api._parametrize_fns(
            unpack_fns=[unpack_fn],
            equal_fns=[equal_fn],
            kwargs={
                "foo": "foo",
                "bar": "barbar",
            },
            aliases={baz_alias: "baz"},
        )

        assert len(parametrized_unpack_fns) == 1
        params = inspect.signature(parametrized_unpack_fns[0]).parameters
        assert params["foo"].default == "foo"

        assert len(parametrized_equal_fns) == 1
        params = inspect.signature(parametrized_equal_fns[0]).parameters
        assert params["bar"].default == "barbar"
        assert params["baz"].default == "baz"

    def test_extra_kwargs(self):
        def unpack_fn(pair, /, *, foo):  # pragma: no cover
            pass

        def equal_fn(pair, /, *, bar):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._parametrize_fns(
                unpack_fns=[unpack_fn],
                equal_fns=[equal_fn],
                kwargs={
                    "foo": "foo",
                    "bar": "bar",
                    "baz": "baz",
                },
                aliases={},
            )

    def test_extra_annotations(self):
        foo_alias = alias.Alias("foo")
        bar_alias = alias.Alias("bar")
        baz_alias = alias.Alias("baz")

        def unpack_fn(pair, /, *, foo: Annotated[Any, foo_alias]):  # pragma: no cover
            pass

        def equal_fn(pair, /, *, bar: Annotated[Any, bar_alias]):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._parametrize_fns(
                unpack_fns=[unpack_fn],
                equal_fns=[equal_fn],
                kwargs={},
                aliases={
                    foo_alias: "foo",
                    bar_alias: "bar",
                    baz_alias: "baz",
                },
            )


class TestBindKwargs:
    def test_bind(self):
        bar_alias = alias.Alias("bar")
        baz_alias = alias.Alias("baz")
        qux_alias = alias.Alias("qux")

        def fn(
            pair,
            /,
            *,
            foo,
            bar_like: Annotated[Any, bar_alias],
            baz="baz",
            qux_like: Annotated[str, qux_alias] = "qux",
        ):  # pragma: no cover
            pass

        bound_fn, bound = api._bind_kwargs(
            fn,
            kwargs={"foo": "foo", "qux_like": "quxqux"},
            aliases={bar_alias: "bar", baz_alias: "bazbaz"},
        )

        params = inspect.signature(bound_fn).parameters
        assert params["foo"].default == "foo"
        assert params["bar_like"].default == "bar"
        assert params["baz"].default == "baz"
        assert params["qux_like"].default == "quxqux"

        assert bound == {"foo", "qux_like", bar_alias}

    def test_missing_required(self):
        def required_param(pair, /, *, param):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._bind_kwargs(required_param, kwargs={}, aliases={})


class TestParseFn:
    def test_no_params(self):
        def no_params():  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._parse_fn(no_params)

    def test_pair_arg_keyword_only(self):
        def pair_arg_keyword_only(*, pair):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._parse_fn(
                pair_arg_keyword_only,
            )

    def test_pair_arg_var_positional(self):
        def pair_arg_var_positional(*args):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._parse_fn(
                pair_arg_var_positional,
            )

    def test_pair_arg_var_keyword(self):
        def pair_arg_var_keyword(**kwargs):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._parse_fn(
                pair_arg_var_keyword,
            )

    def test_param_positional_only(self):
        def param_positional_only(pair, param, /):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._parse_fn(param_positional_only)

    def test_param_var_positional(self):
        def param_var_positional(pair, *params):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._parse_fn(param_var_positional)

    def test_param_var_keyword(self):
        def param_var_keyword(pair, param, **params):  # pragma: no cover
            pass

        with pytest.raises(TypeError, match="^$"):
            api._parse_fn(param_var_keyword)

    def test_parse(self):
        bar_alias = alias.Alias("bar")
        qux_alias = alias.Alias("qux")

        def fn(
            pair,
            /,
            *,
            foo,
            bar_like: Annotated[Any, bar_alias],
            baz="baz",
            qux_like: Annotated[str, qux_alias] = "qux",
        ):  # pragma: no cover
            pass

        available, aliases, required = api._parse_fn(fn)

        assert available == {"foo", "bar_like", "baz", "qux_like"}
        assert aliases == {bar_alias: "bar_like", qux_alias: "qux_like"}
        assert required == {"foo", "bar_like"}


class TestExtractAlias:
    def test_no_annotation(self):
        p = inspect.Parameter(
            name="_",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=inspect.Parameter.empty,
        )
        assert api._extract_alias(p) is None

    def test_no_alias(self):
        p = inspect.Parameter(
            name="_",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[Any, object()],
        )
        assert api._extract_alias(p) is None

    def test_alias(self):
        a = alias.Alias("a")
        b = alias.Alias("b")

        p = inspect.Parameter(
            name="_",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[Any, object(), a, object(), b, object()],
        )
        assert api._extract_alias(p) is a


class TestCompare:
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
