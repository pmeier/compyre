# compyre

## What is this?

`compyre` provides container unpacking and elementwise equality comparisons for arbitrary objects using their native functionality. It offers convenient defaults, while being fully configurable.

!["X all the Y" meme with "compyre all the things" as text](docs/images/meme.png "compyre meme")

## Why do I need it?

Have you ever found yourself in a situation where you needed to test a potentially nested container of values against a reference? [`pytest`](https://docs.pytest.org), the de facto standard test framework for Python, features awesome [failure reporting](https://docs.pytest.org/en/stable/example/reportingdemo.html) for builtin types such as dictionaries, lists, integers, strings, and so on.

But what about other common types that come with their own comparison logic, e.g. [`numpy.ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray) and [`numpy.testing.assert_allclose`](https://numpy.org/doc/stable/reference/generated/numpy.testing.assert_allclose.html)? How do you compare a dictionary or worse a dataclass of these?

- Did you ever skip writing a proper test in such a situation and opted to write a simple, but incomplete one instead?
- If not, did you write the test as loop over the individual elements, and later spend more time debugging, because you have no way of knowing for which element the test failure happened?
- If not, is manually writing out all the assertions and maintaining them keeping you from working on the stuff that actually matters for your application or library?

If you have answered "yes" for any of the questions above, `compyre` was made for you.

## How do I get started?

Most basic cases can be covered by `compyre.equal` or `compyre.assert_equal`. The former provides a boolean check, while the latter raises an `AssertionError` with information what elements mismatch and why.

```python
import dataclasses

import numpy as np

import compyre

@dataclasses.dataclass
class MyObject:
    id: str
    data: list[np.ndarray]

expected = MyObject(
    id="foo",
    data=[np.array([1, 2]), np.array([3, 4])],
)

actual = MyObject(
    id="bar",
    data=[np.array([1, 2]), np.array([3, 5])],
)

compyre.assert_equal(actual, expected)
```

```
AssertionError: comparison resulted in 2 error(s):

id
    AssertionError: 'bar' != 'foo'
data.1
    AssertionError: 
    Not equal to tolerance rtol=1e-07, atol=0

    Mismatched elements: 1 / 2 (50%)
    Max absolute difference among violations: 1
    Max relative difference among violations: 0.25
     ACTUAL: array([3, 5])
     DESIRED: array([3, 4])
```

## How do I learn more?

Please have a look at the [documentation](https://compyre.readthedocs.io/en/stable/).
