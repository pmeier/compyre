import pytest

from compyre._availability import available_if, is_available


def regular_fn():
    return True


@available_if("compyre")
def available_fn():
    return True


@available_if("unavailable_package>=1.2.3,!=4.5.6,<7.8.9")
def unavailable_package_fn():  # pragma: no cover
    pass


@available_if("compyre<0.0.1")
def unavailable_version_fn():  # pragma: no cover
    pass


FNS_AND_AVAILABILITY = [
    (unavailable_version_fn, False),
    (regular_fn, True),
    (available_fn, True),
    (unavailable_package_fn, False),
]


@pytest.mark.parametrize(("fn", "available"), FNS_AND_AVAILABILITY)
def test_if_available_wrapper(fn, available):
    if available:
        assert fn() is True
    else:
        with pytest.raises(RuntimeError):
            fn()


@pytest.mark.parametrize(("fn", "available"), FNS_AND_AVAILABILITY)
def test_is_available(fn, available):
    assert is_available(fn) is available
