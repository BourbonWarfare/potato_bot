# ruff: noqa: F401, F811

import uuid
from contextlib import asynccontextmanager

import aiohttp
import pytest

from bw.interface import BaseClient, User
from bw.missions.types import IterationUuid, MissionUuid
from tests.fixtures.aiohttp_responses import FakeResponse, fake_aiohttp_session
from tests.fixtures.responses import (
    SAMPLE_ITERATION_UUID,
    SAMPLE_MISSION_UUID,
    sample_iteration_payload,
    sample_mission_payload,
)


AUTH_HEADER = {'Authorization': 'Bearer test-token'}


class StubClient(BaseClient):
    """Minimum-viable BaseClient: known auth_header and a backend_session that yields self."""

    def __init__(self, header: dict | None = None):
        self._header = header if header is not None else AUTH_HEADER

    @property
    def auth_header(self) -> dict:
        return self._header

    @asynccontextmanager
    async def backend_session(self, session=None):
        yield self


@pytest.fixture
def patched_port(mocker):
    from bw.environment import ENVIRONMENT

    mocker.patch.object(ENVIRONMENT, 'backend_port', return_value=8080)


@pytest.mark.asyncio
async def test__user__iteration_information__parses_full_payload(patched_port, fake_aiohttp_session, sample_iteration_payload):
    fake_aiohttp_session(FakeResponse(payload=sample_iteration_payload))

    result = await User(StubClient()).iteration_information(IterationUuid(SAMPLE_ITERATION_UUID))

    assert result.iteration == 7
    assert result.bwmf_version == '1.0.0'
    assert result.changelog == {'description': 'Fixed briefing typo'}
    assert result.mission.title == 'tcvm_coop_20'
    assert result.mission.mission_type.name == 'Co-Op'
    assert result.mission.mission_type.signoffs_required == 1


@pytest.mark.asyncio
async def test__user__iteration_information__sends_auth_header(patched_port, fake_aiohttp_session, sample_iteration_payload):
    session = fake_aiohttp_session(FakeResponse(payload=sample_iteration_payload))

    await User(StubClient()).iteration_information(IterationUuid(SAMPLE_ITERATION_UUID))

    assert session.init_headers == AUTH_HEADER
    assert session.calls[0]['headers'] == AUTH_HEADER


@pytest.mark.asyncio
async def test__user__iteration_information__url_includes_iteration_uuid(
    patched_port, fake_aiohttp_session, sample_iteration_payload
):
    session = fake_aiohttp_session(FakeResponse(payload=sample_iteration_payload))

    await User(StubClient()).iteration_information(IterationUuid(SAMPLE_ITERATION_UUID))

    assert str(SAMPLE_ITERATION_UUID) in session.calls[0]['url']


@pytest.mark.asyncio
async def test__user__iteration_information__non_200_raises(patched_port, fake_aiohttp_session):
    fake_aiohttp_session(FakeResponse(status=404))

    with pytest.raises(aiohttp.ClientResponseError):
        await User(StubClient()).iteration_information(IterationUuid(SAMPLE_ITERATION_UUID))


@pytest.mark.asyncio
async def test__user__mission_information__parses_payload(patched_port, fake_aiohttp_session, sample_mission_payload):
    fake_aiohttp_session(FakeResponse(payload=sample_mission_payload))

    result = await User(StubClient()).mission_information(MissionUuid(SAMPLE_MISSION_UUID))

    assert result.title == 'tcvm_coop_20'
    assert result.server == 'main'
    assert result.author_name == 'tcvm'
    assert result.mission_type.name == 'Co-Op'


@pytest.mark.asyncio
async def test__user__mission_information__sends_auth_header(patched_port, fake_aiohttp_session, sample_mission_payload):
    session = fake_aiohttp_session(FakeResponse(payload=sample_mission_payload))

    await User(StubClient()).mission_information(MissionUuid(SAMPLE_MISSION_UUID))

    assert session.init_headers == AUTH_HEADER
    assert session.calls[0]['headers'] == AUTH_HEADER


@pytest.mark.asyncio
async def test__user__mission_information__non_200_raises(patched_port, fake_aiohttp_session):
    fake_aiohttp_session(FakeResponse(status=500))

    with pytest.raises(aiohttp.ClientResponseError):
        await User(StubClient()).mission_information(MissionUuid(SAMPLE_MISSION_UUID))
