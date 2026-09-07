import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import discord

logger = logging.getLogger('bw.potbot.command')

TemporaryWebhookTarget = discord.TextChannel | discord.Thread
TemporaryWebhook = discord.Webhook | discord.Thread


@asynccontextmanager
async def temporary_webhook(
    target: TemporaryWebhookTarget,
    *,
    name: str = 'temporary hook',
    reason: str | None = None,
) -> AsyncIterator[TemporaryWebhook]:
    """Yield a temporary webhook for text channels, deleting it on exit.

    Threads cannot have webhooks created directly, so the thread itself is yielded
    and no cleanup is needed.
    """
    if isinstance(target, discord.Thread):
        yield target
        return

    webhook = await target.create_webhook(name=name, reason=reason)
    try:
        yield webhook
    finally:
        try:
            await webhook.delete(reason=reason)
        except discord.DiscordException:
            logger.warning('Failed to delete temporary webhook [%s]', webhook.id, exc_info=True)
