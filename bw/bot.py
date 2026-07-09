from typing import Self
from pathlib import Path

import logging
import discord
from discord.ext import commands

from bw.commands import community, helpers, mission_making, recruitment, staff, authentication, user
from bw.version import VERSION, Version

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
        await self.add_cog(user.User(self))

        logger.info(f'Setup as {self.user}. Ready to go! :3')

    async def on_ready(self):
        from bw.events.broker import global_event_broker

        version_path = Path('version.txt')

        clear_commands_path = Path('CLEAR_COMMANDS.txt')
        if clear_commands_path.exists():
            logger.info('Found the request to clear all commands. This is expensive, you better have a good reason.')
            for guild_id in [guild.id for guild in self.guilds]:
                guild = discord.Object(id=guild_id)
                self.tree.clear_commands(guild=guild, type=None)
                await self.tree.sync(guild=guild)
            clear_commands_path.unlink()
            # we want to force a re-sync with our true commands, so we delete this file to force it
            version_path.unlink(missing_ok=True)

        if version_path.exists():
            with open(version_path) as f:
                current_version = Version.from_string(f.read())
        else:
            current_version = Version(0, 0, 0)
        with open(version_path, mode='w') as f:
            f.write(f'{VERSION}')

        logger.info(f'Current version: {current_version}')
        if current_version != VERSION:
            logger.info('A new version detected, re-syncing')
            logger.debug(f'current_version={current_version}, VERSION={VERSION}')
            await self.tree.sync()

        logger.info('Starting event broker')
        global_event_broker.start()
        logger.info(f'Session ready for {self.user}')
