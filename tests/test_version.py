from bw.version import Version


def test__version__round_trips_plain_version():
    version = Version(1, 2, 3)

    assert Version.from_string(str(version)) == version


def test__version__round_trips_extra_version():
    version = Version(1, 2, 3, 'beta')

    assert Version.from_string(str(version)) == version


def test__version__invalid_shape_returns_invalid_version():
    assert Version.from_string('not-a-version') == Version(0, 0, 0, 'INVALID')


def test__version__compares_to_its_rendered_form():
    version = Version(1, 2, 3)

    assert version == str(version)


def test__version__does_not_equal_unrelated_type():
    assert Version(1, 2, 3) != 123
