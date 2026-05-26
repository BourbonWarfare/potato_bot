import datetime
import uuid

import pytest

from bw.missions.response import (
    IterationInformationResponse,
    MissionInformationResponse,
    MissionTypeResponse,
)


SAMPLE_MISSION_UUID = uuid.UUID('b3d7e343-d244-45fd-a614-a40e3da5de90')
SAMPLE_ITERATION_UUID = uuid.UUID('11111111-2222-3333-4444-555555555555')
SAMPLE_AUTHOR_UUID = uuid.UUID('aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
SAMPLE_CREATION = datetime.datetime(2026, 1, 1, 12, 0, 0, tzinfo=datetime.UTC)
SAMPLE_UPLOAD = datetime.datetime(2026, 5, 20, 9, 30, 0, tzinfo=datetime.UTC)


@pytest.fixture
def sample_mission_type():
    return MissionTypeResponse(name='Co-Op', signoffs_required=1, tag=1)


@pytest.fixture
def sample_mission(sample_mission_type):
    return MissionInformationResponse(
        uuid=SAMPLE_MISSION_UUID,
        server='main',
        creation_date=SAMPLE_CREATION,
        author_uuid=SAMPLE_AUTHOR_UUID,
        author_name='tcvm',
        title='tcvm_coop_20',
        mission_type=sample_mission_type,
        special_flags={'is_night': True, 'has_armor': False},
    )


@pytest.fixture
def sample_iteration(sample_mission):
    return IterationInformationResponse(
        uuid=SAMPLE_ITERATION_UUID,
        mission=sample_mission,
        min_player_count=15,
        max_player_count=40,
        desired_player_count=30,
        safe_start_length=10,
        mission_length=70,
        upload_date=SAMPLE_UPLOAD,
        bwmf_version='1.0.0',
        iteration=7,
        changelog='Fixed briefing typo',
    )


@pytest.fixture
def sample_iteration_payload():
    """JSON shape returned by /api/v1/missions/iteration/<uuid>. Strings for dates, dict for nested objects."""
    return {
        'uuid': str(SAMPLE_ITERATION_UUID),
        'min_player_count': 15,
        'max_player_count': 40,
        'desired_player_count': 30,
        'safe_start_length': 10,
        'mission_length': 70,
        'upload_date': SAMPLE_UPLOAD.isoformat(),
        'bwmf_version': '1.0.0',
        'iteration': 7,
        'changelog': 'Fixed briefing typo',
        'mission': {
            'uuid': str(SAMPLE_MISSION_UUID),
            'server': 'main',
            'creation_date': SAMPLE_CREATION.isoformat(),
            'author_uuid': str(SAMPLE_AUTHOR_UUID),
            'author_name': 'tcvm',
            'title': 'tcvm_coop_20',
            'special_flags': {'is_night': True},
            'mission_type': {'name': 'Co-Op', 'signoffs_required': 1, 'tag': 1},
        },
    }


@pytest.fixture
def sample_mission_payload(sample_iteration_payload):
    """JSON shape returned by /api/v1/missions/mission/<uuid>. No iteration fields."""
    return sample_iteration_payload['mission']
