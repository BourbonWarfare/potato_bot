from typing import Self
from pathlib import Path

import logging
import discord
from discord.ext import commands

from bw.commands import community, helpers, mission_making, recruitment, staff, authentication
from bw.version import VERSION, Version
from bw.events.broker import global_event_broker

logger = logging.getLogger('bw.potbot')


class PotatoBot(commands.Bot):
    @classmethod
    def setup(cls) -> Self:
        intents = discord.Intents.default()
        return cls(
            intents=intents,
            command_prefix='!',
            allowed_mentions=discord.AllowedMentions(everyone=True, users=True, replied_user=True, roles=True),
        )

    async def setup_hook(self):
        await self.add_cog(community.Community(self))
        await self.add_cog(helpers.Helpers(self))
        await self.add_cog(mission_making.MissionMaking(self))
        await self.add_cog(recruitment.Recruitment(self))
        await self.add_cog(staff.Staff(self))
        await self.add_cog(authentication.Authentication(self))

        logger.info(f'Setup as {self.user}. Ready to go! :3')

    async def on_ready(self):
        path = Path('version.txt')
        if path.exists():
            with open(path) as f:
                current_version = Version.from_string(f.read())
        else:
            current_version = Version(0, 0, 0)
        with open(path, mode='w') as f:
            f.write(f'{VERSION}')

        logger.info(f'Current version: {current_version}')
        if current_version != VERSION:
            logger.info('A new version detected, re-syncing')
            logger.debug(f'current_version={current_version}, VERSION={VERSION}')
            await self.tree.sync()
        
        logger.info('Starting event broker')
        global_event_broker.start()
        logger.info(f'Session ready for {self.user}')
