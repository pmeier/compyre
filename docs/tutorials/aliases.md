# Aliases

This tutorial will teach you what the `aliases` parameter of functions like [compyre.assert_equal][] is and how it is
used.

## Concept

Suppose you want to compare a [float][] as well as [numpy.ndarray][]

```python
import numpy as np

expected = {
    "number": 1.0,
    "array": np.array([2.0, 3.0])
}

actual = {
    "number": 0.9,
    "array": np.array([2.1, 2.8])
}
```

As you can see the values are not actually equal, but only close to each other

```python
from compyre import assert_equal

try:
    assert_equal(actual, expected)
except AssertionError as e:
    print(e)
```

```
comparison resulted in 2 error(s):

number
    AssertionError: Numbers 0.9 and 1.0 are not close!

    Absolute difference: 0.09999999999999998
    Relative difference: 0.09999999999999998 (up to 1e-09 allowed)
array
    AssertionError: 
    Not equal to tolerance rtol=1e-07, atol=0

    Mismatched elements: 2 / 2 (100%)
    Max absolute difference among violations: 0.2
    Max relative difference among violations: 0.06666667
     ACTUAL: array([2.1, 2.8])
     DESIRED: array([2., 3.])
```

As floating point values rarely should be compared for bitwise equality, we need to set appropriate tolerances. Let's
assume for our use case that an absolute tolerance of `0.5` is fine.

The [float][] value is compared by [compyre.builtin.equal_fns.builtins_number][], which internally uses
[math.isclose][]. The [numpy.ndarray][] is compared by [compyre.builtin.equal_fns.numpy_ndarray][], which internally
uses [numpy.testing.assert_allclose][]. Unfortunately, both inner function don't agree on the parameter name for the
absolute tolerance: [math.isclose][] uses `abs_tol`, while [numpy.testing.assert_allclose][] uses `atol`. Meaning, we
can get our check to pass with

```python
assert_equal(actual, expected, abs_tol=0.5, atol=0.5)
```

Since this can be confusing and hard to maintain, `compyre` supports the concept of aliases. An alias can be attached to
each parameter of unpacking or equality check function, e.g. [compyre.builtin.equal_fns.builtins_number][] or
[compyre.builtin.equal_fns.numpy_ndarray][], and can be passed to the outer function, e.g. [compyre.assert_equal][].

```python
from compyre import alias

assert_equal(actual, expected, aliases={alias.ABSOLUTE_TOLERANCE: 0.5})
```

Explicitly passing a keyword argument takes priority of aliases. For example, to compare the [float][] without an
absolute tolerance, but keep it for all other types, we can explicitly pass the `abs_tol` keyword argument alongside the
alias:

```python
try:
    assert_equal(
        actual, expected, aliases={alias.ABSOLUTE_TOLERANCE: 0.5}, abs_tol=0
    )
except AssertionError as e:
    print(e)
```

```
comparison resulted in 1 error(s):

number
    AssertionError: Numbers 0.9 and 1.0 are not close!

    Absolute difference: 0.09999999999999998
    Relative difference: 0.09999999999999998 (up to 1e-09 allowed)
```

## Built-in aliases

`compyre` currently supports the following aliases:

- [compyre.alias.RELATIVE_TOLERANCE][]
- [compyre.alias.ABSOLUTE_TOLERANCE][]
- [compyre.alias.NAN_EQUALITY][]

All functions from [compyre.builtin.unpack_fns][] and [compyre.builtin.equal_fns][] respect them where applicable.

## Custom aliases

Depending on your use case, you might want to introduce custom aliases. Suppose you have a concept "Foo" that is
applicable to multiple equality check functions. You start by creating an alias for that.

```python
from compyre import alias

FOO = alias.Alias("foo")
```

!!! tip

    Passing a name to the alias, e.g. `"foo"` above, is optional, but encouraged to ease debugging.

Suppose further that the equality check functions while being able to handle the concept "Foo", they take the value
under different parameters, e.g. `bar` and `baz`. To apply the alias use it as part of a [typing.Annotated][]
annotation.

```python
from typing import Annotated

import compyre.api

def bool_equal_fn(p: compyre.api.Pair, /, *, bar: Annotated[str, FOO]) -> compyre.api.EqualFnResult:
    if not (isinstance(p.actual, bool) and isinstance(p.expected, bool)):
        return None

    print(f"bool_equal_fn got {bar=}")

    return p.actual is p.expected

def int_equal_fn(p: compyre.api.Pair, /, *, baz: Annotated[str, FOO]) -> compyre.api.EqualFnResult:
    if not (isinstance(p.actual, int) and isinstance(p.expected, int)):
        return None

    print(f"int_equal_fn got {baz=}")

    return p.actual == p.expected
```

Let's build a custom `assert_equal` function that uses our equality check functions and also is able to unpack
dictionaries, so we can pass multiple values at the same time.

```python
import functools

import compyre.builtin.unpack_fns

assert_equal = functools.partial(
    compyre.api.assert_equal,
    unpack_fns=[compyre.builtin.unpack_fns.collections_mapping],
    equal_fns=[
        bool_equal_fn,
        int_equal_fn,
    ],
)
```

Calling it while passing a value for the `FOO` alias, we can observe that it is properly passed down as `bar` for
`bool_equal_fn` and as `baz` for `int_equal_fn`.

```python
value = {"bool": False, "int": 1}

assert_equal(value, value, aliases={FOO: "foo"})
```

```
bool_equal_fn got bar='foo'
int_equal_fn got baz='foo'
```

Passing a value for `bar` or `baz` directly takes priority over the alias:

```python
assert_equal(value, value, aliases={FOO: "foo"}, baz="baz")
```

```
bool_equal_fn got bar='foo'
int_equal_fn got baz='baz'
```
