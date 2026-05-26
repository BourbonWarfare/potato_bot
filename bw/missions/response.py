import dataclasses
import datetime
import typing
from bw.missions.types import MissionTypeTag, IterationUuid, UserUuid
from dataclasses import dataclass
from typing import Any


@dataclass
class _CoerceFields:
    def __post_init__(self):
        hints = typing.get_type_hints(type(self))
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            field_type = hints[field.name]
            check_type = typing.get_origin(field_type) or field_type

            if isinstance(value, check_type):
                continue

            if check_type is datetime.datetime and isinstance(value, str):
                value = datetime.datetime.fromisoformat(value)
            elif dataclasses.is_dataclass(check_type) and isinstance(value, dict):
                value = check_type(**value)
            else:
                value = check_type(value)

            setattr(self, field.name, value)


@dataclass
class MissionUploadResponse(_CoerceFields):
    iteration_number: int
    min_players: int
    max_players: int
    desired_players: int
    safe_start_length: int
    mission_length: int


@dataclass
class MissionTypeResponse(_CoerceFields):
    name: str
    signoffs_required: int
    tag: MissionTypeTag


@dataclass
class MissionInformationResponse(_CoerceFields):
    uuid: IterationUuid
    server: str
    creation_date: datetime.datetime
    author_uuid: UserUuid
    author_name: str
    title: str
    mission_type: MissionTypeResponse
    special_flags: dict[str, Any]


@dataclass
class IterationInformationResponse(_CoerceFields):
    uuid: IterationUuid
    mission: MissionInformationResponse
    min_player_count: int
    max_player_count: int
    desired_player_count: int
    safe_start_length: int
    mission_length: int
    upload_date: datetime.datetime
    bwmf_version: str
    iteration: int
    changelog: str
