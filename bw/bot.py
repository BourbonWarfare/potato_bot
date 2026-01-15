from typing import Self

import logging
import discord

from bw.commands import community, helpers, mission_making, recruitment
from bw.version import VERSION, Version

logger = logging.getLogger('bw.potbot')


class PotatoBot(discord.ext.commands.Bot):
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
        with open('state.settings', mode='r') as f:
            current_version = Version.from_string(f.read())
        with open('state.settings', mode='w') as f:
            f.write(f'version={VERSION}')
        
        logger.info(f'Current version: {current_version}')
        if current_version != VERSION:
            logger.info(f'A new version detected, re-syncing')
            logger.debug(f'current_version{current_version}, VERSION={VERSION}')
            self.tree.sync()
        logger.info(f'Session ready for {self.user}')
