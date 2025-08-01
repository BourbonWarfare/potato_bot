from typing import Self

import logging
import discord

logger = logging.getLogger('bw.potbot')


class PotatoBot(discord.Client):
    @classmethod
    def setup(cls) -> Self:
        intents = discord.Intents.default()
        return cls(
            intents=intents,
            command_prefix='!',
        )

    async def on_setup(self):
        logger.info(f'Setup as {self.user}')

    async def on_ready(self):
        logger.info(f'Session ready for {self.user}')
