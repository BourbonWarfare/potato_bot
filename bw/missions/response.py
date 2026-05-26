import dataclasses
from bw.missions.types import MissionTypeTag, IterationUuid, UserUuid
from dataclasses import dataclass
from typing import Any
from pydoc import locate
import datetime


@dataclass
class MissionUploadResponse:
    iteration_number: int
    min_players: int
    max_players: int
    desired_players: int
    safe_start_length: int
    mission_length: int

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            field_type = field.type if not isinstance(field.type, str) else locate(field.type)
            assert isinstance(field_type, type)
            if not isinstance(value, field_type):
                setattr(self, field.name, field_type(value))


@dataclass
class MissionTypeResponse:
    name: str
    signoffs_required: int
    tag: MissionTypeTag

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            field_type = field.type if not isinstance(field.type, str) else locate(field.type)
            assert isinstance(field_type, type)
            if not isinstance(value, field_type):
                setattr(self, field.name, field_type(value))


@dataclass
class MissionInformationResponse:
    uuid: IterationUuid
    server: str
    creation_date: datetime.datetime
    author_uuid: UserUuid
    author_name: str
    title: str
    mission_type: MissionTypeResponse
    special_flags: dict[str, Any]

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            field_type = field.type if not isinstance(field.type, str) else locate(field.type)
            assert isinstance(field_type, type)
            if not isinstance(value, field_type):
                setattr(self, field.name, field_type(value))


@dataclass
class IterationInformationResponse:
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

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            field_type = field.type if not isinstance(field.type, str) else locate(field.type)
            assert isinstance(field_type, type)
            if not isinstance(value, field_type):
                setattr(self, field.name, field_type(value))
