from bw.version import Version


def test__version__stringifies_plain_version():
    assert str(Version(1, 2, 3)) == '1.2.3'


def test__version__stringifies_extra_version():
    assert str(Version(1, 2, 3, 'beta')) == '1.2.3-beta'


def test__version__from_string__parses_plain_version():
    assert Version.from_string('1.2.3') == Version(1, 2, 3)


def test__version__from_string__parses_extra_version():
    assert Version.from_string('1.2.3-beta') == Version(1, 2, 3, 'beta')


def test__version__from_string__invalid_shape_returns_invalid_version():
    assert Version.from_string('not-a-version') == Version(0, 0, 0, 'INVALID')


def test__version__compares_to_string():
    assert Version(1, 2, 3) == '1.2.3'


def test__version__does_not_equal_unrelated_type():
    assert Version(1, 2, 3) != 123
