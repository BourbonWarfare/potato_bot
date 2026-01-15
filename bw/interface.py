import aiohttp
import asyncio
import functools
import random
from contextlib import asynccontextmanager
from bw.environment import ENVIRONMENT
from bw.endpoints import Root

def backoff(delay=2, retries=3):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_retry = 0
            current_delay = delay
            while current_retry < retries:
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    current_retry += 1
                    if current_retry >= retries:
                        raise e
                    await asyncio.sleep(current_delay + random.random() * delay)
                    current_delay *= 2

        return wrapper

    return decorator


class Client:
    session_url: str
    bot_token: str
    session_token: str | None

    def __init__(self, session_url: str):
        self.session_url = session_url
        self.bot_token = ENVIRONMENT.backend_token()
        self.session_token = None

    @backoff(delay=0.5, retries=5)
    async def refresh_session(self, session: None | aiohttp.ClientSession = None):
        async def refresh(session: aiohttp.ClientSession):
            async with session.get(self.session_url, json={'bot_token': self.bot_token}) as response:
                if response.status != 200:
                    self.session_token = None
                else:
                    self.session_token = (await response.json()).get('session_token')

        if session is None:
            async with aiohttp.ClientSession() as session:
                await refresh(session)
        else:
            await refresh(session)

    @asynccontextmanager
    async def api_session(self, session: aiohttp.ClientSession | None = None):
        if self.session_token is None:
            await self.refresh_session(session)
        yield self

    @property
    def auth_header(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {self.session_token}'} if self.session_token else {}


class Interface:
    client: Client

    def __init__(self):
        self.address = 'localhost'
        self.port = ENVIRONMENT.backend_port()
        self.client = Client(self.url(Root.get().api.v1.auth.login.bot.resolve()))

    def url(self, path: str) -> str:
        return f'http://{self.address}:{self.port}{path}'

    async def healthcheck(self) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url(Root.get().api.v1.healthcheck.resolve())) as response:
                return response.status == 200

    async def start_arma_server(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with self.client.api_session(session) as client:
                async with session.post(
                    self.url(Root.get().api.v1.server_ops.arma.server.var(server).start.resolve()), headers=client.auth_header
                ) as response:
                    return response.status == 200

    async def stop_arma_server(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with self.client.api_session(session) as client:
                async with session.post(
                    self.url(Root.get().api.v1.server_ops.arma.server.var(server).stop.resolve()), headers=client.auth_header
                ) as response:
                    return response.status == 200

    async def restart_arma_server(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with self.client.api_session(session) as client:
                async with session.post(
                    self.url(Root.get().api.v1.server_ops.arma.server.var(server).restart.resolve()), headers=client.auth_header
                ) as response:
                    return response.status == 200

    async def update_arma_server(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with self.client.api_session(session) as client:
                async with session.post(
                    self.url(Root.get().api.v1.server_ops.arma.server.var(server).update.resolve()), headers=client.auth_header
                ) as response:
                    return response.status == 200

    async def update_arma_server_mods(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with self.client.api_session(session) as client:
                async with session.post(
                    self.url(Root.get().api.v1.server_ops.arma.server.var(server).update_mods.resolve()),
                    headers=client.auth_header,
                ) as response:
                    return response.status == 200

    async def arma_server_healthcheck(self, server: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url(Root.get().api.v1.server_ops.arma.server.var(server).healthcheck.resolve())
            ) as response:
                return response.status == 200
