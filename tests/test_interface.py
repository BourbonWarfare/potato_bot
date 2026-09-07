# ruff: noqa: F401, F811

import uuid
from contextlib import asynccontextmanager
from typing import Any

import aiohttp
import pytest

from bw.interface import BaseClient, User, server_url
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


class RefreshingClient(BaseClient):
    def __init__(self):
        self.token = 'old-token'
        self.refreshes = 0

    @property
    def auth_header(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {self.token}'}

    async def refresh_session(self):
        self.refreshes += 1
        self.token = 'new-token'


class SequentialSession:
    def __init__(self, responses: list[FakeResponse]):
        self.responses = responses
        self.calls: list[dict[str, Any]] = []
        self.init_headers: dict[str, str] = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def get(self, url: str, **kwargs):
        self.calls.append({'method': 'GET', 'url': url, **kwargs})
        return self.responses.pop(0)


@pytest.fixture
def patched_port(mocker):
    from bw.environment import ENVIRONMENT

    mocker.patch.object(ENVIRONMENT, 'backend_port', return_value=8080)


@pytest.mark.asyncio
async def test__server_url__uses_configured_backend_address_and_port(mocker):
    from bw.environment import ENVIRONMENT

    mocker.patch.object(ENVIRONMENT, 'backend_address', return_value='backend.example.test')
    mocker.patch.object(ENVIRONMENT, 'backend_port', return_value=1234)

    assert server_url('/api/v1/healthcheck') == 'http://backend.example.test:1234/api/v1/healthcheck'


@pytest.mark.asyncio
async def test__user__iteration_information__refreshes_and_retries_once_after_unauthorized(
    patched_port, mocker, sample_iteration_payload
):
    client = RefreshingClient()
    session = SequentialSession([FakeResponse(status=401), FakeResponse(payload=sample_iteration_payload)])

    def constructor(*args, headers=None, **kwargs):
        session.init_headers = headers or {}
        return session

    mocker.patch('aiohttp.ClientSession', side_effect=constructor)

    result = await User(client).iteration_information(IterationUuid(SAMPLE_ITERATION_UUID))

    assert result.iteration == 7
    assert client.refreshes == 1
    assert [call['headers'] for call in session.calls] == [
        {'Authorization': 'Bearer old-token'},
        {'Authorization': 'Bearer new-token'},
    ]


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
