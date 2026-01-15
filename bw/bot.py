from typing import Self

import logging
import discord

from bw.commands import community, helpers, mission_making, recruitment

logger = logging.getLogger('bw.potbot')


class PotatoBot(discord.Client):
    @classmethod
    def setup(cls) -> Self:
        intents = discord.Intents.default()
        return cls(
            intents=intents,
            command_prefix='!',
        )

    async def setup_hook(self):
        await self.add_cog(community.Community(self))
        await self.add_cog(helpers.Helpers(self))
        await self.add_cog(mission_making.MissionMaking(self))
        await self.add_cog(recruitment.Recruitment(self))

        logger.info(f'Setup as {self.user}. Ready to go! :3')

    async def on_ready(self):
        logger.info(f'Session ready for {self.user}')
