from bw.interface import Interface
import aiohttp
from aiohttp import hdrs
import logging
from typing import Any
from collections.abc import Callable
from functools import wraps
from discord.ext import tasks

from bw.endpoints.root import Root

logger = logging.getLogger('bw.events')

class Broker:
    def __init__(self):
        pass

    def start(self):
        self.backend_event_handler.start()

    def stop(self):
        self.backend_event_handler.stop()

    def add_handler(self, handler: Callable[[str, str, dict[str, Any]], None], namespace: str | None, event: str | None):
        pass

    def subscribe(self, *, namespace: str | None = None, event: str | None = None):
        def decorator(func: Callable[[str, str, dict[str, Any]], None]):
            @wraps(func)
            def wrapper(*args, **kwargs) -> None:
                return func(*args, **kwargs)

            global_event_broker.add_handler(wrapper, namespace=namespace, event=event)
            return wrapper
        
        return decorator

    @tasks.loop()
    async def backend_event_handler(self):
        timeout = aiohttp.ClientTimeout(total=None, sock_read=None)
        url = Interface().url(Root.get().api.v1.realtime.sse.resolve())
        headers={hdrs.ACCEPT: 'text/event-stream', hdrs.CACHE_CONTROL: 'no-cache'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, timeout=timeout, headers=headers) as response:
                response.raise_for_status()
                if response.status == 204:
                    logger.info('SSE stream has no content')
                    return
                async for line_in_bytes in response.content:
                    line = line_in_bytes.decode('utf-8')
                    print(line_in_bytes, line)

global_event_broker = Broker()
