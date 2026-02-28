import asyncio
import logging
import aiohttp
import datetime
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

logger = logging.getLogger('bw.arma_server_cache')


class ArmaServerCache:
    servers_: list[str]
    refresh_task_: None | asyncio.Task
    last_refresh_: None | datetime.datetime

    def __init__(self):
        self.servers_ = []
        self.refresh_task_ = None
        self.last_refresh_ = None

    async def refresh(self):
        from bw.interface import Interface

        try:
            logger.info('Refreshing server cache')
            servers = await Interface().get_arma_servers()
            self.last_refresh_ = datetime.datetime.now()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectionError) as e:
            logger.warning(f'Could not get arma servers: {e}')
            servers = []
        self.servers_ = servers
        self.refresh_task_ = None

    @property
    def blocking_servers(self) -> list[str]:
        if not self.last_refresh_:
            asyncio.run(self.refresh())
        return self.servers_

    @property
    @asynccontextmanager
    async def servers(self) -> AsyncIterator[list[str]]:
        if self.servers_ is None:
            await self.refresh()

        yield self.servers_

        if self.last_refresh_ is not None:
            time_since_refresh = datetime.datetime.now() - self.last_refresh_
        else:
            time_since_refresh = datetime.timedelta(days=1000)

        if not self.refresh_task_ and time_since_refresh >= datetime.timedelta(minutes=5):
            self.refresh_task_ = asyncio.create_task(self.refresh())
