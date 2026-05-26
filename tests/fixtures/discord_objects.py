"""Minimal stand-ins for discord.py objects. They are not subclasses — tests check
that our code calls them with the right shape, not that discord.py renders things
correctly."""

from dataclasses import dataclass, field
from typing import Any

import pytest


@dataclass
class FakeForumTag:
    name: str
    id: int = 0


@dataclass
class FakeMessage:
    content: str | None = None
    embed: Any = None
    embeds: list = field(default_factory=list)


class FakeThread:
    """Stand-in for discord.Thread. Records every send() call."""

    def __init__(self, id: int = 999):
        self.id = id
        self.sent: list[FakeMessage] = []

    async def send(self, content: str | None = None, *, embed=None, embeds=None, **_: Any) -> FakeMessage:
        message = FakeMessage(content=content, embed=embed, embeds=embeds or [])
        self.sent.append(message)
        return message


class FakeForumChannel:
    """Stand-in for discord.ForumChannel. Records create_thread calls and returns a FakeThread."""

    def __init__(self, available_tags: list[FakeForumTag] | None = None, new_thread_id: int = 999):
        self.available_tags: list[FakeForumTag] = available_tags or []
        self.create_thread_calls: list[dict[str, Any]] = []
        self._new_thread_id = new_thread_id

    async def create_thread(self, *, name: str, embeds=None, reason: str | None = None, applied_tags=None, **kwargs):
        call = {'name': name, 'embeds': embeds, 'reason': reason, 'applied_tags': applied_tags or [], **kwargs}
        self.create_thread_calls.append(call)
        thread = FakeThread(id=self._new_thread_id)
        return thread, None


class FakeBot:
    """Stand-in for discord.ext.commands.Bot. Channels are pre-registered by id."""

    def __init__(self, channels: dict[int, Any] | None = None):
        self.channels = channels or {}

    def get_channel(self, channel_id: int) -> Any:
        return self.channels.get(channel_id)


@pytest.fixture
def fake_thread():
    return FakeThread()


@pytest.fixture
def fake_forum_channel():
    return FakeForumChannel(
        available_tags=[FakeForumTag(name='Co-Op', id=1), FakeForumTag(name='TVT', id=2)],
        new_thread_id=999,
    )


@pytest.fixture
def fake_bot(fake_forum_channel):
    return FakeBot(channels={12345: fake_forum_channel})
