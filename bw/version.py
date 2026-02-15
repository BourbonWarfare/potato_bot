from typing import Self


class Version:
    _major: int
    _minor: int
    _patch: int
    _extra: str | None

    def __init__(self, major: int, minor: int, patch: int, extra: str | None = None):
        self._major = major
        self._minor = minor
        self._patch = patch
        self._extra = extra

    @classmethod
    def from_string(cls, string: str) -> Self:
        components = string.split('.')
        if len(components) == 3:
            return Version(
                int(components[0]),
                int(components[1]),
                int(components[2]),
            )
        elif len(components) == 4:
            return Version(
                int(components[0]),
                int(components[1]),
                int(components[2]),
                components[3],
            )
        else:
            return Version(0, 0, 0, 'INVALID')

    def __str__(self) -> str:
        if self._extra is None:
            return f'{self._major}.{self._minor}.{self._patch}'
        else:
            return f'{self._major}.{self._minor}.{self._patch}-{self._extra}'

    def __eq__(self, other: Self | str) -> bool:
        if isinstance(other, Version):
            return (
                self._major == other._major
                and self._minor == other._minor
                and self._patch == other._patch
                and self._extra == other._extra
            )
        else:
            return str(self) == other


VERSION = Version(1, 0, 6)
