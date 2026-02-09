import aiohttp
import asyncio
import functools
import random
import datetime
from contextlib import asynccontextmanager
from bw.environment import ENVIRONMENT
from bw.endpoints import Root
from bw.session.api import SessionApi
from bw.state import State
from bw.session.oauth import OAuthSession, BwSession
from bw.error import RefreshFailed
from bw.utils import backoff

class ApiClient:
    session_url: str
    bot_token: str
    session: BwSession

    def __init__(self, session_url: str):
        self.session_url = session_url
        self.bot_token = ENVIRONMENT.backend_token()
        self.session = BwSession.null()

    @backoff(delay=0.5, retries=5)
    async def refresh_session(self, session: None | aiohttp.ClientSession = None):
        async def refresh(session: aiohttp.ClientSession):
            async with session.get(self.session_url, json={'bot_token': self.bot_token}) as response:
                response.raise_for_status()
                session = await response.json()
                self.session.expire_time = datetime.datetime.fromisoformat(session.get('expire_time'))
                self.session.token = session.get('session_token')

        if session is None:
            async with aiohttp.ClientSession() as session:
                await refresh(session)
        else:
            await refresh(session)

    @asynccontextmanager
    async def api_session(self, session: aiohttp.ClientSession | None = None):
        if self.session.is_expired():
            await self.refresh_session(session)
        yield self

    @property
    def auth_header(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {self.session_token}'} if self.session_token else {}


class UserClient:
    discord_session: OAuthSession
    bw_session: BwSession

    def __init__(self, oauth_session: OAuthSession):
        self.discord_session = oauth_session
        self.bw_session = BwSession.null()

    @backoff(delay=0.5, retries=5)
    async def refresh_session(self):
        self.discord_session = await SessionApi().refresh_oauth_session(State.state, self.refresh_token)
        self.bw_session = await SessionApi().login_to_backend(State.state, self.discord_session)

    @asynccontextmanager
    async def user_session(self):
        if self.bw_session.is_expired() or self.discord_session.is_expired():
            await self.refresh_session()

        try:
            yield self
        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                await self.refresh_session(self.refresh_token)
            else:
                raise e

    @property
    def auth_header(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {self.bw_session.token}'}


class Interface:
    def __init__(self):
        self.address = 'localhost'
        self.port = ENVIRONMENT.backend_port()

    def url(self, path: str) -> str:
        return f'http://{self.address}:{self.port}{path}'

    async def healthcheck(self) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url(Root.get().api.v1.healthcheck.resolve())) as response:
                return response.status == 200

    async def arma_server_healthcheck(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url(Root.get().api.v1.server_ops.arma.server.var(server).healthcheck.resolve())
            ) as response:
                return response.status == 200
    
    async def auth_get_access_code(self, state: str) -> dict:
        headers = {'Authorization': f'Bearer {state}'}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                self.url(Root.get().api.v1.auth.login.discord.resolve())
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def login_to_backend(self, oauth_session: OAuthSession) -> dict:
        async with aiohttp.ClientSession(headers=oauth_session.as_header()) as session:
            async with session.post(
                self.url(Root.get().api.v1.auth.login.discord.resolve())
            ) as response:
                response.raise_for_status()
                return await response.json()

class User(Interface):
    def __init__(self, oauth_session: OAuthSession):
        self.client = UserClient(oauth_session)
        super().__init__()

    async def start_arma_server(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with self.client.user_session() as client:
                async with session.post(
                    self.url(Root.get().api.v1.server_ops.arma.server.var(server).start.resolve()), headers=client.auth_header
                ) as response:
                    return response.status == 200

    async def stop_arma_server(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with self.client.user_session() as client:
                async with session.post(
                    self.url(Root.get().api.v1.server_ops.arma.server.var(server).stop.resolve()), headers=client.auth_header
                ) as response:
                    return response.status == 200

    async def restart_arma_server(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with self.client.user_session() as client:
                async with session.post(
                    self.url(Root.get().api.v1.server_ops.arma.server.var(server).restart.resolve()), headers=client.auth_header
                ) as response:
                    return response.status == 200

    async def update_arma_server(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with self.client.user_session() as client:
                async with session.post(
                    self.url(Root.get().api.v1.server_ops.arma.server.var(server).update.resolve()), headers=client.auth_header
                ) as response:
                    return response.status == 200

    async def update_arma_server_mods(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with self.client.user_session() as client:
                async with session.post(
                    self.url(Root.get().api.v1.server_ops.arma.server.var(server).update_mods.resolve()),
                    headers=client.auth_header,
                ) as response:
                    return response.status == 200
