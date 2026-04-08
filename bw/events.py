from bw.interface import Interface
import aiohttp
from typing import Any
from collections.abc import Callable
from functools import wraps
from discord.ext import tasks

from bw.endpoints.root import Root

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
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url=url, headers={'Accept': 'text/event-stream'}) as response:
                response.raise_for_status()
                print(dict(response.headers))
                async for line in response.content:
                    print(line)

global_event_broker = Broker()
