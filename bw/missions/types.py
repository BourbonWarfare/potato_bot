import uuid


class MissionTypeTag(int):
    def __new__(cls, value: int | str) -> "MissionTypeTag":
        return super().__new__(cls, int(value))

    def __repr__(self) -> str:
        return f"MissionTypeTag({super().__repr__()})"


class IterationUuid(uuid.UUID):
    def __init__(self, value: str | uuid.UUID | bytes) -> None:
        if isinstance(value, uuid.UUID):
            super().__init__(int=value.int)
        elif isinstance(value, bytes):
            super().__init__(bytes=value)
        else:
            super().__init__(hex=str(value))

    def __repr__(self) -> str:
        return f"IterationUuid('{super().__str__()}')"


class MissionUuid(uuid.UUID):
    def __init__(self, value: str | uuid.UUID | bytes) -> None:
        if isinstance(value, uuid.UUID):
            super().__init__(int=value.int)
        elif isinstance(value, bytes):
            super().__init__(bytes=value)
        else:
            super().__init__(hex=str(value))

    def __repr__(self) -> str:
        return f"MissionUuid('{super().__str__()}')"


class UserUuid(uuid.UUID):
    def __init__(self, value: str | uuid.UUID | bytes) -> None:
        if isinstance(value, uuid.UUID):
            super().__init__(int=value.int)
        elif isinstance(value, bytes):
            super().__init__(bytes=value)
        else:
            super().__init__(hex=str(value))

    def __repr__(self) -> str:
        return f"UserUuid('{super().__str__()}')"
