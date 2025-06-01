from compyre import alias


def test_str():
    name = "sentinel"
    a = alias.Alias(name)

    assert str(a) == name


def test_repr_smoke():
    name = "sentinel"
    a = alias.Alias(name)

    assert name in repr(a)
    assert len(repr(a)) > len(str(a))
