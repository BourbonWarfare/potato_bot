import datetime
import json
import logging
import uuid
from abc import ABC
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiohttp

from bw.endpoints import Root
from bw.environment import ENVIRONMENT
from bw.error import CannotReachBwBackend, ResponseError
from bw.missions.response import (
    IterationInformationResponse,
    MissionInformationResponse,
    MissionTypeResponse,
    MissionUploadResponse,
)
from bw.missions.types import IterationUuid, MissionUuid
from bw.session.oauth import BwSession, OAuthSession
from bw.utils import backoff

logger = logging.getLogger('bw.interface')


def server_url(path: str) -> str:
    address = ENVIRONMENT.backend_address()
    port = ENVIRONMENT.backend_port()
    return f'http://{address}:{port}{path}'


class BaseClient(ABC):
    @asynccontextmanager
    async def backend_session(self, session: aiohttp.ClientSession | None = None):
        yield self

    async def ensure_session(self, session: aiohttp.ClientSession | None = None) -> None:
        return None

    async def refresh_session(self, session: aiohttp.ClientSession | None = None) -> None:
        return None

    @property
    def auth_header(self) -> dict[str, str]:
        return {}


class ApiClient(BaseClient):
    bot_token: str
    session: BwSession | None

    def __init__(self):
        self.bot_token = ENVIRONMENT.backend_bot_token()
        self.session = None

    async def ensure_session(self, session: aiohttp.ClientSession | None = None) -> None:
        if not self.session or self.session.is_expired():
            await self.refresh_session(session)

    @backoff(delay=0.5, retries=5)
    async def refresh_session(self, session: None | aiohttp.ClientSession = None) -> None:
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
        await self.ensure_session(session)
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

    async def ensure_session(self, session: aiohttp.ClientSession | None = None) -> None:
        if self.bw_session.is_expired() or self.discord_session.is_expired():
            await self.refresh_session()

    @backoff(delay=0.5, retries=5)
    async def refresh_session(self, session: aiohttp.ClientSession | None = None) -> None:
        from bw.session.api import SessionApi
        from bw.state import State

        self.discord_session = await SessionApi().refresh_oauth_session(State.state, self.discord_session)
        self.bw_session = await SessionApi().login_to_backend(State.state, self.discord_session)

    @asynccontextmanager
    async def backend_session(self, session: aiohttp.ClientSession | None = None):
        await self.ensure_session(session)
        try:
            yield self
        except aiohttp.ClientConnectionError as e:
            logger.error(f'Cannot reach BW Backend: {e}')
            raise CannotReachBwBackend() from e

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
            async with (
                aiohttp.ClientSession() as session,
                session.get(server_url(Root.get().api.v1.server_ops.arma.server.var(server).healthcheck.resolve())) as response,
            ):
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

    async def _request(
        self,
        method: str,
        url: str,
        *,
        parser,
        retry_unauthorized: bool = True,
        response_error: bool = False,
        **kwargs,
    ):
        await self.client.ensure_session()
        headers = {**self.client.auth_header, **kwargs.pop('headers', {})}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                request = getattr(session, method)
                async with request(url, headers=headers, **kwargs) as response:
                    try:
                        err_body = await response.text() if response_error else ''
                        response.raise_for_status()
                    except aiohttp.ClientResponseError as e:
                        if e.status == 401 and retry_unauthorized:
                            logger.warning('Session expired during request. Refreshing and retrying once...')
                            await self.client.refresh_session()
                            return await self._request(
                                method,
                                url,
                                parser=parser,
                                retry_unauthorized=False,
                                response_error=response_error,
                                **kwargs,
                            )
                        if response_error:
                            raise ResponseError(err_body, e) from e
                        raise
                    return await parser(response)
        except aiohttp.ClientConnectionError as e:
            logger.error(f'Cannot reach BW Backend: {e}')
            raise CannotReachBwBackend() from e

    async def _json(self, method: str, url: str, **kwargs):
        async def parser(response):
            return await response.json()

        return await self._request(method, url, parser=parser, **kwargs)

    async def _text(self, method: str, url: str, **kwargs) -> str:
        async def parser(response):
            return await response.text()

        return await self._request(method, url, parser=parser, **kwargs)

    async def _empty(self, method: str, url: str, **kwargs) -> None:
        async def parser(_response):
            return None

        return await self._request(method, url, parser=parser, **kwargs)

    async def get_groups(self) -> dict:
        return await self._json('get', server_url(Root.get().api.v1.group.list.resolve()))

    async def join_group(self, group: str):
        payload = {'group_name': group}
        await self._empty('post', server_url(Root.get().api.v1.group.join.resolve()), json=payload, response_error=True)

    async def get_arma_server_rpt(self, server: str) -> tuple[str, str]:
        async def parser(response):
            disposition = response.headers.get('content-disposition', '')
            filenames = [line.strip() for line in disposition.split(';') if 'filename' in line]
            filename = filenames[0].split('=')[1].strip('"') if filenames else ''
            return (await response.text(), filename)

        return await self._request(
            'get', server_url(Root.get().api.v1.server_ops.arma.server.var(server).rpt.resolve()), parser=parser
        )

    async def start_arma_server(self, server: str) -> dict:
        return await self._json('post', server_url(Root.get().api.v1.server_ops.arma.server.var(server).start.resolve()))

    async def stop_arma_server(self, server: str) -> dict:
        return await self._json('post', server_url(Root.get().api.v1.server_ops.arma.server.var(server).stop.resolve()))

    async def restart_arma_server(self, server: str) -> dict:
        return await self._json('post', server_url(Root.get().api.v1.server_ops.arma.server.var(server).restart.resolve()))

    async def update_arma_server(self, server: str) -> dict:
        return await self._json('post', server_url(Root.get().api.v1.server_ops.arma.server.var(server).update.resolve()))

    async def update_arma_mod_by_id(self, workshop_id: int):
        await self._empty(
            'post', server_url(Root.get().api.v1.server_ops.arma.mod.workshop_id.var(str(workshop_id)).update.resolve())
        )

    async def update_arma_server_mods(self, server: str) -> dict:
        async def parser(response):
            affected_servers = {}
            updated_mods = []
            async for line in response.content:
                if not line.strip():
                    continue
                loaded_json = json.loads(line)
                if 'affected_servers' in loaded_json:
                    affected_servers = loaded_json
                else:
                    updated_mods.append(loaded_json)
            return {'affected_servers': affected_servers, 'updated_mods': updated_mods}

        return await self._request(
            'post', server_url(Root.get().api.v1.server_ops.arma.server.var(server).update_mods.resolve()), parser=parser
        )

    async def get_arma_server_status(self, server: str) -> dict:
        return await self._json('get', server_url(Root.get().api.v1.server_ops.arma.server.var(server).status.resolve()))

    async def upload_mission(self, mission_path: Path, server: str, changelog: dict[str, str]) -> MissionUploadResponse:
        payload = {'pbo_path': str(mission_path), 'changelog': changelog}

        async def parser(response):
            return MissionUploadResponse(**await response.json())

        return await self._request(
            'post',
            server_url(Root.get().api.v1.missions.upload.server.var(server).resolve()),
            parser=parser,
            json=payload,
            response_error=True,
        )

    async def force_upload_mission(self, mission_path: Path, server: str) -> None:
        payload = {'pbo_path': str(mission_path), 'changelog': {}, 'play_in_session': False}
        await self._empty(
            'post',
            server_url(Root.get().api.v1.missions.upload.server.var(server).resolve()),
            json=payload,
            response_error=True,
        )

    async def iteration_information(self, iteration_uuid: IterationUuid) -> IterationInformationResponse:
        payload: dict[str, Any] = await self._json(
            'get', server_url(Root.get().api.v1.missions.iteration.iteration_id.var(str(iteration_uuid)).resolve())
        )
        mission: dict[str, Any] = payload.pop('mission')
        tag: dict[str, Any] = mission.pop('mission_type')

        mission['uuid'] = uuid.UUID(hex=mission['uuid'])
        mission['creation_date'] = datetime.datetime.fromisoformat(mission['creation_date'])
        mission['author_uuid'] = uuid.UUID(hex=mission['author_uuid'])

        return IterationInformationResponse(
            **payload, mission=MissionInformationResponse(**mission, mission_type=MissionTypeResponse(**tag))
        )

    async def mission_information(self, mission_uuid: MissionUuid) -> MissionInformationResponse:
        payload: dict[str, Any] = await self._json(
            'get', server_url(Root.get().api.v1.missions.mission.mission_id.var(str(mission_uuid)).resolve())
        )
        tag: dict[str, Any] = payload.pop('mission_type')

        payload['uuid'] = uuid.UUID(hex=payload['uuid'])
        payload['author_uuid'] = uuid.UUID(hex=payload['author_uuid'])
        payload['creation_date'] = datetime.datetime.fromisoformat(payload['creation_date'])

        return MissionInformationResponse(**payload, mission_type=MissionTypeResponse(**tag))

    async def get_squad_tag(self) -> dict[str, Any]:
        return await self._json('get', server_url(Root.get().api.v1.user.remark.resolve()))

    async def set_squad_tag(self, profile_name: str, nickname: str | None, steam_id: str, remark: str | None):
        payload = {'profile-name': profile_name, 'nickname': nickname, 'steam-id': steam_id, 'remark': remark}
        await self._empty('post', server_url(Root.get().api.v1.user.remark.resolve()), data=payload)
