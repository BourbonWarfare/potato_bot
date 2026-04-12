import aiohttp
import logging
import json

from aiohttp import hdrs
from collections.abc import Callable
from functools import wraps
from discord.ext import tasks
from dataclasses import dataclass

from bw.interface import Interface
from bw.endpoints.root import Root
from bw.events.decoder import ServerSentEventBuilder, ServerSentEvent

logger = logging.getLogger('bw.events')


@dataclass
class Handler:
    handler: Callable[[ServerSentEvent], None]
    filtered_namespace: str | None
    filtered_event: str | None


class Broker:
    handlers: list[Handler]

    def __init__(self):
        self.handlers = []

    def start(self):
        self.backend_event_handler.start()

    def stop(self):
        self.backend_event_handler.stop()

    def add_handler(self, handler: Callable[[ServerSentEvent], None], namespace: str | None, event: str | None):
        self.handlers.append(Handler(handler=handler, filtered_namespace=namespace, filtered_event=event))

    def subscribe(self, *, namespace: str | None = None, event: str | None = None):
        def decorator(func: Callable[[ServerSentEvent], None]):
            @wraps(func)
            def wrapper(*args, **kwargs) -> None:
                return func(*args, **kwargs)

            global_event_broker.add_handler(wrapper, namespace=namespace, event=event)
            return wrapper

        return decorator

    def publish(self, event: ServerSentEvent):
        for handler in self.handlers:
            print(handler.filtered_namespace, handler.filtered_event, event)
            if handler.filtered_namespace and event.namespace != handler.filtered_namespace:
                continue
            if handler.filtered_event and event.event != handler.filtered_event:
                continue

            handler.handler(event)

    @tasks.loop()
    async def backend_event_handler(self):
        timeout = aiohttp.ClientTimeout(total=None, sock_read=None)
        url = Interface().url(Root.get().api.v1.realtime.sse.resolve())
        headers = {hdrs.ACCEPT: 'text/event-stream', hdrs.CACHE_CONTROL: 'no-cache'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, timeout=timeout, headers=headers) as response:
                response.raise_for_status()
                if response.status == 204:
                    logger.info('SSE stream has no content')
                    return

                latest_event = ServerSentEventBuilder()
                async for line_in_bytes in response.content:
                    line = line_in_bytes.decode('utf-8').strip('\n').strip('\r')
                    if line == '':
                        self.publish(latest_event.finish())
                        latest_event = ServerSentEventBuilder()
                        continue

                    prefix, following = line.split(':', 1)
                    if prefix == 'id':
                        latest_event.with_id(following.strip())
                    elif prefix == 'event':
                        latest_event.with_event(following.strip())
                    elif prefix == 'data':
                        latest_event.with_data(json.loads(following.strip()))


global_event_broker = Broker()
