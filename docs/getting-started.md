# Getting started

## Installation

You can install `compyre` from [PyPI](https://pypi.org/project/compyre/) with your favorite tool, e.g.

```shell
pip install compyre
```

## Quick start

Most basic cases can be covered by [compyre.is_equal][] or [compyre.assert_equal][]. The former provides a boolean check, while the latter raises an `AssertionError` with information what elements mismatch and why.

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
