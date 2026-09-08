
import pytest

from bw.commands.webhooks import temporary_webhook
from tests.fixtures.discord_objects import FakeThread


class FakeWebhook:
    def __init__(self):
        self.deleted = False
        self.delete_reasons: list[str | None] = []
        self.id = 123

    async def delete(self, *, reason: str | None = None):
        self.deleted = True
        self.delete_reasons.append(reason)


class FakeTextChannel:
    def __init__(self):
        self.created_webhook = FakeWebhook()
        self.create_calls: list[dict] = []

    async def create_webhook(self, *, name: str, reason: str | None = None):
        self.create_calls.append({'name': name, 'reason': reason})
        return self.created_webhook


@pytest.fixture
def patched_thread_type(mocker):
    mocker.patch('bw.commands.webhooks.discord.Thread', FakeThread)


@pytest.mark.asyncio
async def test__temporary_webhook__text_channel_deletes_webhook_on_success(patched_thread_type):
    channel = FakeTextChannel()

    async with temporary_webhook(channel, name='login helper', reason='short lived') as followup:
        assert followup is channel.created_webhook

    assert channel.create_calls == [{'name': 'login helper', 'reason': 'short lived'}]
    assert channel.created_webhook.deleted is True
    assert channel.created_webhook.delete_reasons == ['short lived']


@pytest.mark.asyncio
async def test__temporary_webhook__text_channel_deletes_webhook_on_error(patched_thread_type):
    channel = FakeTextChannel()

    with pytest.raises(RuntimeError):
        async with temporary_webhook(channel):
            raise RuntimeError('boom')

    assert channel.created_webhook.deleted is True


@pytest.mark.asyncio
async def test__temporary_webhook__thread_is_used_directly_without_creating_webhook(patched_thread_type):
    thread = FakeThread()

    async with temporary_webhook(thread) as followup:
        assert followup is thread

    assert thread.sent == []
