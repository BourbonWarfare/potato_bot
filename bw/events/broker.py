import asyncio
import json
import logging
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import aiohttp
from aiohttp import hdrs
from discord.ext import tasks

from bw.endpoints.root import Root
from bw.events.decoder import ServerSentEvent, ServerSentEventBuilder
from bw.interface import server_url

logger = logging.getLogger('bw.events')


def apply_sse_line(builder: ServerSentEventBuilder, line: str) -> ServerSentEventBuilder:
    if line.startswith(':') or ':' not in line:
        logger.debug('Ignoring SSE line without a field: %r', line)
        return builder

    prefix, following = line.split(':', 1)
    value = following.strip()
    if prefix == 'id':
        builder.with_id(value)
    elif prefix == 'event':
        builder.with_event(value)
    elif prefix == 'data':
        builder.with_data(json.loads(value))
    else:
        logger.debug('Ignoring unsupported SSE field %r', prefix)
    return builder


@dataclass
class Handler:
    handler: Callable[[ServerSentEvent], Awaitable[None]]
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

    def add_handler(self, handler: Callable[[ServerSentEvent], Awaitable[None]], *, namespace: str | None, event: str | None):
        self.handlers.append(Handler(handler=handler, filtered_namespace=namespace, filtered_event=event))

    async def publish(self, event: ServerSentEvent):
        for handler in self.handlers:
            if handler.filtered_namespace and event.namespace != handler.filtered_namespace:
                logger.debug(
                    'Filtering handler due to namespace mismatch:'
                    f'Expected: "{event.namespace}". Handler: "{handler.filtered_namespace}"'
                )
                continue
            if handler.filtered_event and event.event != handler.filtered_event:
                logger.debug(
                    f'Filtering handler due to event mismatch: Expected: "{event.event}". Handler: "{handler.filtered_event}"'
                )
                continue

            try:
                await handler.handler(event)
            except Exception:
                logger.exception('Failed to run event handler')

    async def _get_sse(self, session: aiohttp.ClientSession, tasks: asyncio.TaskGroup):
        timeout = aiohttp.ClientTimeout(total=None, sock_read=None)
        url = server_url(Root.get().api.v1.realtime.sse.resolve())
        headers = {hdrs.ACCEPT: 'text/event-stream', hdrs.CACHE_CONTROL: 'no-cache'}

        async with session.get(url=url, timeout=timeout, headers=headers) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as err:
                logging.warning(f'An error occured while retrieving event: {err}')
                return

            if response.status == 204:
                logger.info('SSE stream has no content')
                return

            latest_event = ServerSentEventBuilder()
            async for line_in_bytes in response.content:
                line = line_in_bytes.decode('utf-8').strip('\n').strip('\r')
                if line == '':
                    tasks.create_task(self.publish(latest_event.finish()))
                    latest_event = ServerSentEventBuilder()
                    continue

                apply_sse_line(latest_event, line)

    @tasks.loop(seconds=15, name='sse loop')
    async def backend_event_handler(self):
        async with asyncio.TaskGroup() as tasks, aiohttp.ClientSession() as session:
            while True:
                try:
                    await self._get_sse(session, tasks)
                except aiohttp.ClientConnectionError as err:
                    logging.warning(f'Cannot connect to backend: {err}')
                    await asyncio.sleep(1 + 5 * random.random())
                except aiohttp.ServerConnectionError as err:
                    logging.warning(f'Lost connection to backend: {err}')
                    await asyncio.sleep(1 + 5 * random.random())
                except Exception as err:
                    logging.warning(f'An error occured while handling SSE stream: {err}')
                    await asyncio.sleep(1 + 5 * random.random())


global_event_broker = Broker()
