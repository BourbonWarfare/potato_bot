import asyncio
import logging
import aiohttp
import datetime
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from bw.error import CannotReachBwBackend

logger = logging.getLogger('bw.arma_server_cache')


class GroupCache:
    groups_: list[str]
    refresh_task_: None | asyncio.Task
    last_refresh_: None | datetime.datetime

    def __init__(self):
        self.groups_ = []
        self.refresh_task_ = None
        self.last_refresh_ = None

    async def refresh(self):
        from bw.interface import User
        from bw.state import State

        interface = User(State.state.api_client)

        try:
            logger.info('Refreshing group cache')
            groups = [group['name'] for group in (await interface.get_groups())['groups']]
            self.last_refresh_ = datetime.datetime.now()
        except (aiohttp.ClientResponseError, CannotReachBwBackend) as e:
            logger.warning(f'Could not get groups: {e}')
            groups = []
        self.groups_ = groups
        self.refresh_task_ = None

    @property
    def blocking_groups(self) -> list[str]:
        if not self.last_refresh_:
            asyncio.run(self.refresh())
        return self.groups_

    @property
    @asynccontextmanager
    async def groups(self) -> AsyncIterator[list[str]]:
        if not self.groups_:
            await self.refresh()

        yield self.groups_

        if self.last_refresh_ is not None:
            time_since_refresh = datetime.datetime.now() - self.last_refresh_
        else:
            time_since_refresh = datetime.timedelta(days=1000)

        if not self.refresh_task_ and time_since_refresh >= datetime.timedelta(minutes=5):
            self.refresh_task_ = asyncio.create_task(self.refresh())
