import uuid
from abc import ABC
from bw.missions.types import IterationUuid, MissionUuid
import aiohttp
import datetime
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any
from bw.environment import ENVIRONMENT
from bw.endpoints import Root
from bw.session.oauth import OAuthSession, BwSession
from bw.utils import backoff
from bw.missions.response import (
    MissionUploadResponse,
    IterationInformationResponse,
    MissionInformationResponse,
    MissionTypeResponse,
)
from bw.error import ResponseError, CannotReachBwBackend

logger = logging.getLogger('bw.interface')


def server_url(path: str) -> str:
    address = 'localhost'
    port = ENVIRONMENT.backend_port()
    return f'http://{address}:{port}{path}'


class BaseClient(ABC):
    @asynccontextmanager
    async def backend_session(self, session: aiohttp.ClientSession | None = None):
        yield

    @property
    def auth_header(self) -> dict[str, str]:
        return {}


class ApiClient(BaseClient):
    bot_token: str
    session: BwSession | None

    def __init__(self):
        self.bot_token = ENVIRONMENT.backend_bot_token()
        self.session = None

    @backoff(delay=0.5, retries=5)
    async def refresh_session(self, session: None | aiohttp.ClientSession = None):
        async def refresh(session: aiohttp.ClientSession):
            async with session.post(
                server_url(Root.get().api.v1.auth.login.bot.resolve()), json={'bot_token': self.bot_token}
            ) as response:
                response.raise_for_status()
                session = await response.json()
                self.session = BwSession(
                    token=session['session_token'], expire_time=datetime.datetime.fromisoformat(session['expire_time'])
                )

        if session is None:
            async with aiohttp.ClientSession() as session:
                await refresh(session)
        else:
            await refresh(session)

    @asynccontextmanager
    async def backend_session(self, session: aiohttp.ClientSession | None = None):
        if not self.session or self.session.is_expired():
            await self.refresh_session(session)
        yield self

    @property
    def auth_header(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {self.session.token}'} if self.session else {}


class UserClient(BaseClient):
    bw_session: BwSession
    discord_session: OAuthSession

    def __init__(self, bw_session: BwSession, oauth_session: OAuthSession):
        self.bw_session = bw_session
        self.discord_session = oauth_session

    @backoff(delay=0.5, retries=5)
    async def refresh_session(self):
        from bw.state import State
        from bw.session.api import SessionApi

        self.discord_session = await SessionApi().refresh_oauth_session(State.state, self.discord_session)
        self.bw_session = await SessionApi().login_to_backend(State.state, self.discord_session)

    @asynccontextmanager
    async def backend_session(self, session: aiohttp.ClientSession | None = None):
        if self.bw_session.is_expired() or self.discord_session.is_expired():
            await self.refresh_session()

        try:
            yield self
        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                logger.warning('Session expired after we already started the request. Refreshing...')
                await self.refresh_session()
            else:
                raise e
        except aiohttp.ClientConnectionError as e:
            logger.error(f'Cannot reach BW Backend: {e}')
            raise CannotReachBwBackend()

    @property
    def auth_header(self) -> dict[str, str]:
        return self.bw_session.as_header()


class Interface:
    def __init__(self):
        self.address = 'localhost'
        self.port = ENVIRONMENT.backend_port()

    async def healthcheck(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(server_url(Root.get().api.v1.healthcheck.resolve())) as response:
                    return response.status == 200
        except aiohttp.ClientConnectionError as e:
            logger.error(f'Cannot reach BW Backend: {e}')
            raise CannotReachBwBackend()

    async def arma_server_healthcheck(self, server: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    server_url(Root.get().api.v1.server_ops.arma.server.var(server).healthcheck.resolve())
                ) as response:
                    return response.status == 200
        except aiohttp.ClientConnectionError as e:
            logger.error(f'Cannot reach BW Backend: {e}')
            raise CannotReachBwBackend()

    async def auth_get_access_code(self, state: str) -> dict:
        headers = {'Authorization': f'Bearer {state}'}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(server_url(Root.get().api.v1.auth.login.discord.resolve())) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientConnectionError as e:
            logger.error(f'Cannot reach BW Backend: {e}')
            raise CannotReachBwBackend()

    async def login_to_backend(self, oauth_session: OAuthSession) -> dict:
        try:
            async with aiohttp.ClientSession(headers=oauth_session.as_header()) as session:
                async with session.post(server_url(Root.get().api.v1.auth.login.discord.resolve())) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientConnectionError as e:
            logger.error(f'Cannot reach BW Backend: {e}')
            raise CannotReachBwBackend()

    async def get_arma_servers(self) -> list[str]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(server_url(Root.get().api.v1.server_ops.arma.servers.resolve())) as response:
                    response.raise_for_status()
                    return (await response.json()).get('servers')
        except aiohttp.ClientConnectionError as e:
            logger.error(f'Cannot reach BW Backend: {e}')
            raise CannotReachBwBackend()


class User(Interface):
    def __init__(self, client: BaseClient):
        self.client = client
        super().__init__()

    async def start_arma_server(self, server: str) -> dict:
        async with aiohttp.ClientSession(headers=self.client.auth_header) as session:
            async with self.client.backend_session(session=session):
                async with session.post(
                    server_url(Root.get().api.v1.server_ops.arma.server.var(server).start.resolve())
                ) as response:
                    response.raise_for_status()
                    return await response.json()

    async def stop_arma_server(self, server: str) -> dict:
        async with aiohttp.ClientSession(headers=self.client.auth_header) as session:
            async with self.client.backend_session(session=session):
                async with session.post(
                    server_url(Root.get().api.v1.server_ops.arma.server.var(server).stop.resolve())
                ) as response:
                    response.raise_for_status()
                    return await response.json()

    async def restart_arma_server(self, server: str) -> dict:
        async with aiohttp.ClientSession(headers=self.client.auth_header) as session:
            async with self.client.backend_session(session=session):
                async with session.post(
                    server_url(Root.get().api.v1.server_ops.arma.server.var(server).restart.resolve())
                ) as response:
                    response.raise_for_status()
                    return await response.json()

    async def update_arma_server(self, server: str) -> dict:
        async with aiohttp.ClientSession(headers=self.client.auth_header) as session:
            async with self.client.backend_session(session=session):
                async with session.post(
                    server_url(Root.get().api.v1.server_ops.arma.server.var(server).update.resolve())
                ) as response:
                    response.raise_for_status()
                    return await response.json()

    async def update_arma_server_mods(self, server: str) -> dict:
        async with aiohttp.ClientSession(headers=self.client.auth_header) as session:
            async with self.client.backend_session(session=session) as client:
                async with session.post(
                    server_url(Root.get().api.v1.server_ops.arma.server.var(server).update_mods.resolve()),
                    headers=client.auth_header,
                ) as response:
                    response.raise_for_status()
                    return await response.json()

    async def get_arma_server_status(self, server: str) -> dict:
        async with aiohttp.ClientSession(headers=self.client.auth_header) as session:
            async with self.client.backend_session(session=session) as client:
                async with session.get(
                    server_url(Root.get().api.v1.server_ops.arma.server.var(server).status.resolve()),
                    headers=client.auth_header,
                ) as response:
                    response.raise_for_status()
                    return await response.json()

    async def upload_mission(self, mission_path: Path, server: str, changelog: dict[str, str]) -> MissionUploadResponse:
        payload = {'pbo_path': str(mission_path), 'changelog': changelog}
        async with aiohttp.ClientSession(headers=self.client.auth_header) as session:
            async with self.client.backend_session(session=session) as client:
                async with session.post(
                    server_url(Root.get().api.v1.missions.upload.server.var(server).resolve()),
                    headers=client.auth_header,
                    json=payload,
                ) as response:
                    try:
                        err_body = await response.text()
                        response.raise_for_status()
                    except aiohttp.ClientResponseError as e:
                        raise ResponseError(err_body, e)
                    return MissionUploadResponse(**await response.json())

    async def iteration_information(self, iteration_uuid: IterationUuid) -> IterationInformationResponse:
        async with aiohttp.ClientSession(headers=self.client.auth_header) as session:
            async with self.client.backend_session(session=session) as client:
                async with session.get(
                    server_url(Root.get().api.v1.missions.iteration.iteration_id.var(str(iteration_uuid)).resolve()),
                    headers=client.auth_header,
                ) as response:
                    response.raise_for_status()
                    payload: dict[str, Any] = await response.json()
                    mission: dict[str, Any] = payload.pop('mission')
                    tag: dict[str, Any] = mission.pop('mission_type')

                    mission['uuid'] = uuid.UUID(hex=mission['uuid'])
                    mission['creation_date'] = datetime.datetime.fromisoformat(mission['creation_date'])
                    mission['author_uuid'] = uuid.UUID(hex=mission['author_uuid'])

                    return IterationInformationResponse(
                        **payload, mission=MissionInformationResponse(**mission, mission_type=MissionTypeResponse(**tag))
                    )

    async def mission_information(self, mission_uuid: MissionUuid) -> MissionInformationResponse:
        async with aiohttp.ClientSession(headers=self.client.auth_header) as session:
            async with self.client.backend_session(session=session) as client:
                async with session.get(
                    server_url(Root.get().api.v1.missions.mission.mission_id.var(str(mission_uuid)).resolve()),
                    headers=client.auth_header,
                ) as response:
                    response.raise_for_status()
                    payload: dict[str, Any] = await response.json()
                    tag: dict[str, Any] = payload.pop('mission_type')

                    payload['uuid'] = uuid.UUID(hex=payload['uuid'])
                    payload['author_uuid'] = uuid.UUID(hex=payload['author_uuid'])
                    payload['creation_date'] = datetime.datetime.fromisoformat(payload['creation_date'])

                    return MissionInformationResponse(**payload, mission_type=MissionTypeResponse(**tag))
