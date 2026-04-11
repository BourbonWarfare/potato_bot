from bw.missions.types import MissionTypeTag, IterationUuid, UserUuid
from dataclasses import dataclass
from typing import Any
import datetime


@dataclass
class MissionUploadResponse:
    iteration_number: int
    min_players: int
    max_players: int
    desired_players: int
    safe_start_length: int
    mission_length: int


@dataclass
class MissionTypeResponse:
    name: str
    signoffs_required: int
    tag: MissionTypeTag


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

