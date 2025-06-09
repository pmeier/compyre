# Customization

While the default functionality of [compyre.is_equal][] and [compyre.assert_equal][] should be good enough for common
use cases, we acknowledge the fact that they cannot cover everything. We designed `compyre` with this in mind and also
provide a fully customizable API that can be tailored to your needs.

In this tutorial you learn about custom unpacking and equality check functions, how to implement, and how to integrate
them into `compyre`.

## Unpacking functions

Unpacking functions are set through the `unpack_fns` parameter and are iterated in order until the first non-[None][]
result:

- If the result is list of [compyre.api.Pair][]s, they are added to the beginning of the processing queue
resulting in a depth-first traversal of the inputs.
- If the result is an [Exception][], it is stored and further processing for the pair is skipped.

Suppose you want to compare two [numpy.ndarray][]s.

```
import numpy as np

expected = np.array([1, 2, 3])
actual = np.array([1, 3, -3])
```

Simplified, [compyre.assert_equal][] for this use case is equivalent to

```python
import compyre.api
import compyre.builtin

try:
    compyre.api.assert_equal(
        actual,
        expected,
        unpack_fns=[],
        equal_fns=[compyre.builtin.equal_fns.numpy_ndarray]
    )
except AssertionError as e:
    print(e)
```

```
comparison resulted in 1 error(s):


    AssertionError: 
    Not equal to tolerance rtol=1e-07, atol=0

    Mismatched elements: 2 / 3 (66.7%)
    Max absolute difference among violations: 6
    Max relative difference among violations: 2.
     ACTUAL: array([ 1,  3, -3])
     DESIRED: array([1, 2, 3])
```

Suppose that you rather want to compare the numbers elementwise similar to a list. This can be achieved with a simple
unpacking function that uses [numpy.ndarray.tolist][] and [compyre.builtin.unpack_fns.collections_sequence][] to create
the pairs with the correct index information.

```
def unpack_array(p: compyre.api.Pair) -> api.UnpackFnResult:
    # both inputs have to be arrays for this function to try to unpack them
    if not (isinstance(p.actual, np.ndarray) and isinstance(p.expected, np.ndarray)):
        return None
        
    return compyre.builtin.unpack_fns.collections_sequence(
        compyre.api.Pair(index=p.index, actual=p.actual.tolist(), expected=p.expected.tolist())
    )
```

Using [compyre.builtin.equal_fns.builtins_number][] as the equality check function, the elementwise equality check can
be achieved with

```python
try:
    compyre.api.assert_equal(
        actual,
        expected,
        unpack_fns=[unpack_array],
        equal_fns=[compyre.builtin.equal_fns.builtins_number]
    )
except AssertionError as e:
    print(e)
```

```
comparison resulted in 2 error(s):

1
    AssertionError: Numbers 3 and 2 are not close!

    Absolute difference: 1
    Relative difference: 0.3333333333333333 (up to 1e-09 allowed)
2
    AssertionError: Numbers -3 and 3 are not close!

    Absolute difference: 6
    Relative difference: 2.0 (up to 1e-09 allowed)
```

As written, only one-dimensional arrays can be unpacked. For multi-dimensional arrays we get back a nested list of
elements that `unpack_array` cannot unpack further nor [compyre.builtin.equal_fns.builtins_number][] can compare.

```python
expected = np.array([[1, 2], [3, 4]])
actual = np.array([[1, 2], [4, 4]])

try:
    compyre.api.assert_equal(
        actual,
        expected,
        unpack_fns=[unpack_array],
        equal_fns=[compyre.builtin.equal_fns.builtins_number]
    )
except compyre.api.CompyreError as e:
    print(e)
```

```
0
    CompyreError: unable to compare [1, 2] of type <class 'list'> and [1, 2] of type <class 'list'>
1
    CompyreError: unable to compare [4, 4] of type <class 'list'> and [3, 4] of type <class 'list'>
```

To overcome this, we could refactor `unpack_array` to return a flattened list of all elements. However, this is rather
cumbersome. An easier solution is to include [compyre.builtin.unpack_fns.collections_sequence][] in the unpacking
functions.

```python
try:
    compyre.api.assert_equal(
        actual,
        expected,
        unpack_fns=[
            unpack_array,
            compyre.builtin.unpack_fns.collections_sequence,
        ],
        equal_fns=[compyre.builtin.equal_fns.builtins_number]
    )
except AssertionError as e:
    print(e)
```

```
comparison resulted in 1 error(s):

1.0
    AssertionError: Numbers 4 and 3 are not close!

    Absolute difference: 1
    Relative difference: 0.25 (up to 1e-09 allowed)
```

Equipped with this knowledge and under the assumption that
[compyre.builtin.unpack_fns.collections_sequence][] or something equivalent is always present in the unpacking
functions, we can even simplify `unpack_array` further.

```python
def unpack_array_simple(p: compyre.api.Pair) -> api.UnpackFnResult:
    # both inputs have to be arrays for this function to try to unpack them
    if not (isinstance(p.actual, np.ndarray) and isinstance(p.expected, np.ndarray)):
        return None
        
    return [
        compyre.api.Pair(index=p.index, actual=p.actual.tolist(), expected=p.expected.tolist())
    ]

try:
    compyre.api.assert_equal(
        actual,
        expected,
        unpack_fns=[
            unpack_array_simple,
            compyre.builtin.unpack_fns.collections_sequence,
        ],
        equal_fns=[compyre.builtin.equal_fns.builtins_number]
    )
except AssertionError as e:
    print(e)
```

```
comparison resulted in 1 error(s):

1.0
    AssertionError: Numbers 4 and 3 are not close!

    Absolute difference: 1
    Relative difference: 0.25 (up to 1e-09 allowed)
```

## Equality check functions

Unpacking functions are set through the `equal_fns` parameter and are iterated in order until the first non-[None][]
result:

- If the result is [True][], the input pair is considered equal
- If the result is [False][] or any [Exception][], the input pair is considered not equal. In the former case an
  [AssertionError][] with a default error message is used.

Suppose you want to compare dictionaries only by their keys and lists only by their length rather than unpacking them
and compare their values elementwise.

```python
import dataclasses

@dataclasses.dataclass
class Container:
  dct: dict
  lst: list

expected = Container(dct={"foo": "foo", "bar": "barbar"}, lst=[0, 1, 2])
actual = Container(dct={"foo": "foo", "baz": "barbar"}, lst=[0, 1])
```


This can be achieved with two simple equality check functions

```python
import compyre.api

def dict_keys(p: compyre.api.Pair) -> compyre.api.EqualFnResult:
  if not (isinstance(p.actual, dict) and isinstance(p.expected, dict)):
    return None
  
  if p.actual.keys() == p.expected.keys():
    return True
  else:
    return AssertionError(f"{p.actual.keys()=} != {p.expected.keys()=}")

def list_len(p: compyre.api.Pair) -> compyre.api.EqualFnResult:
  if not (isinstance(p.actual, list) and isinstance(p.expected, list)):
    return None
  
  return len(p.actual) == len(p.expected)
```

Using [compyre.builtin.unpack_fns.dataclasses_dataclass][] as the unpacking function, the key and length check can be
achieved with

```python
try:
    compyre.api.assert_equal(
        actual,
        expected,
        unpack_fns=[compyre.builtin.unpack_fns.dataclasses_dataclass],
        equal_fns=[
            dict_keys,
            list_len,
        ],
    )
except AssertionError as e:
    print(e)
```

```
comparison resulted in 2 error(s):

dct
    AssertionError: p.actual.keys()=dict_keys(['foo', 'baz']) != p.expected.keys()=dict_keys(['foo', 'bar'])
lst
    AssertionError: [0, 1] is not equal to [0, 1, 2]
```

Note that while returning [False][] from `list_len` instead of an [Exception][] with a custom error message, resulted
in the inequality that we wanted, the default error message is not great. One cannot derive from it that the values are
actually irrelevant.

## Parameters

All functions from [compyre.builtin.unpack_fns][] and [compyre.builtin.equal_fns][] as well as all the unpacking and
equality check functions in this tutorial so far do not require any parameters. However, that is not a limitation.

Suppose you want to implement an equality function that checks strings either for equality or just their length. You
could implement it like

```python
import compyre.api

def string_equal(p: compyre.api.Pair, /, *, len_only: bool) -> compyre.api.EqualFnResult:
    if not (isinstance(p.actual, str) and isinstance(p.expected, str)):
        return None

    if len_only:
        return len(p.actual) == len(p.expected)
    else:
        return p.actual == p.expected
```

Calling [compyre.api.assert_equal][] as we have before now results in a [TypeError][] as the `len_only` parameter is not
passed

```python
expected = "foo"
actual = "bar"

try:
    compyre.api.assert_equal(
        actual,
        expected,
        unpack_fns=[],
        equal_fns=[string_equal],
    )
except TypeError as e:
    print(e)
```

```
missing 1 keyword-only argument(s): 'len_only'
```

We can just pass it as keyword argument to [compyre.api.assert_equal][]

```python
compyre.api.assert_equal(
    actual,
    expected,
    unpack_fns=[],
    equal_fns=[string_equal],
    len_only=True,
)
```

To avoid subtle errors, a [TypeError][] is also raised if keyword argument is passed that is not used by any unpacking
or equality check function.

```python
try:
    compyre.api.assert_equal(
        actual,
        expected,
        unpack_fns=[],
        equal_fns=[],
        len_only=True,
    )
except TypeError as e:
    print(e)
```

## Low-level API

If the customisation options detailed so far in this tutorial are still not sufficient for your use case, you can base
your logic on the low-level [compyre.api.compare][]. Everything discussed above is still valid, but instead of a
boolean check like [compyre.api.is_equal][] or an equality assertion like [compyre.api.assert_equal][],
[compyre.api.compare][] returns the list of [Exception][]s returned of the unpacking or equality check functions. Thus,
you have the option to post-filter, produce custom combined error message, and so on.
