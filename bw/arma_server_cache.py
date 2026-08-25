import asyncio
import datetime
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aiohttp

from bw.error import CannotReachBwBackend

logger = logging.getLogger('bw.arma_server_cache')


class ArmaServerCache:
    servers_: list[str]
    refresh_task_: None | asyncio.Task
    last_refresh_: None | datetime.datetime

    def __init__(self):
        self.servers_ = []
        self.refresh_task_ = None
        self.last_refresh_ = None

    async def refresh(self) -> list[str]:
        from bw.interface import Interface

        try:
            logger.info('Refreshing server cache')
            servers = await Interface().get_arma_servers()
            self.last_refresh_ = datetime.datetime.now()
        except (aiohttp.ClientResponseError, CannotReachBwBackend) as e:
            logger.warning(f'Could not get arma servers: {e}')
            servers: list[str] = []
        self.servers_ = servers
        self.refresh_task_ = None

        return self.servers_

    @property
    def blocking_servers(self) -> list[str]:
        if not self.last_refresh_:
            asyncio.run(self.refresh())
        return self.servers_

    @property
    @asynccontextmanager
    async def servers(self) -> AsyncIterator[list[str]]:
        if not self.servers_:
            await self.refresh()

        yield self.servers_

        if self.last_refresh_ is not None:
            time_since_refresh = datetime.datetime.now() - self.last_refresh_
        else:
            time_since_refresh = datetime.timedelta(days=1000)

        if not self.refresh_task_ and time_since_refresh >= datetime.timedelta(minutes=5):
            self.refresh_task_ = asyncio.create_task(self.refresh())
