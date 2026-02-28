from dataclasses import dataclass


@dataclass
class MissionUploadResponse:
    iteration_number: int
    min_players: int
    max_players: int
    desired_players: int
    safe_start_length: int
    mission_length: int
