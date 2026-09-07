import logging
from enum import StrEnum

import discord
from discord import app_commands
from discord.ext import commands

from bw.commands.discord_utils import require_guild, require_member, require_role, require_text_channel
from bw.embeds import call_orientator, get_generic_handbook, get_member_handbook, get_recruit_handbook, not_a_recruit
from bw.environment import ENVIRONMENT
from bw.utils import strip_emoji

logger = logging.getLogger('bw.potbot.command')


class Handbooks(StrEnum):
    RECRUIT = '📘 Recruit Handbook 😕'
    MEMBER = '📗 Member Handbook 🔫'


class Recruitment(commands.Cog, name='Recruitment'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='handbook', description='Links to our handbooks.')
    @app_commands.choices(handbook=[app_commands.Choice(name=choice.value, value=choice.value) for choice in Handbooks])
    @app_commands.describe(handbook='The handbook you want to view.')
    async def handbook(self, interaction: discord.Interaction, handbook: str):
        handbook = Handbooks(handbook)
        logger.info(f'{interaction.user} requested the handbook "{strip_emoji(handbook.name)}".')
        logger.debug(f'handbook given: name={strip_emoji(handbook.name)}, value={strip_emoji(handbook.value)}')
        if handbook.value == Handbooks.RECRUIT:
            logger.debug('fetching recruit handbook')
            await interaction.response.send_message(embed=get_recruit_handbook(), ephemeral=True)
        elif handbook.value == Handbooks.MEMBER:
            logger.debug('fetching member handbook')
            await interaction.response.send_message(embed=get_member_handbook(), ephemeral=True)
        else:
            logger.debug('fetching generic handbook')
            await interaction.response.send_message(embed=get_generic_handbook(), ephemeral=True)

    @app_commands.command(name='orientation', description='Request an orientation')
    async def orientation(self, interaction: discord.Interaction):
        member = require_member(interaction)
        guild = require_guild(interaction)
        if member.get_role(ENVIRONMENT.recruit_role()) is not None:
            logger.info(f'{member} requested an orientation.')
            await interaction.response.send_message(embed=call_orientator())

            if member.get_role(ENVIRONMENT.awaiting_orientation_role()) is None:
                logger.info(f'Adding awaiting orientation role to {member}.')
                try:
                    awaiting_orientation_role = require_role(
                        guild, ENVIRONMENT.awaiting_orientation_role(), 'awaiting_orientation_role_id'
                    )
                    await member.add_roles(awaiting_orientation_role, reason='Requested an orientation.')
                except discord.Forbidden as e:
                    logger.warning(f'Cannot add role: {e}')
            else:
                logger.info(f'{member} already has the awaiting orientation role.')

            channel = require_text_channel(self.bot, ENVIRONMENT.recruitment_channel(), 'recruitment_channel_id')
            role = require_role(guild, ENVIRONMENT.orientor_role(), 'orientation_role_id')
            logger.debug(f'{role.mention}, {member.nick}, {member.global_name}')
            logger.debug(f'{channel}, {channel.name}, {channel.id}, {channel.type}')
            try:
                if member.nick:
                    await channel.send(
                        rf"""📣 {role.mention} a new recruit is requesting orientation.
        Please reach out to {member.nick} ({member.global_name}) to arrange an orientation."""
                    )
                else:
                    await channel.send(
                        rf"""📣 {role.mention} a new recruit is requesting orientation.
        Please reach out to {member.global_name} to arrange an orientation."""
                    )
            except discord.Forbidden as e:
                logger.warning(f'Could not send message: {e}')
        else:
            await interaction.response.send_message(embed=not_a_recruit(), ephemeral=True)
