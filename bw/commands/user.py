import discord
import logging
from discord import app_commands
from discord.ext import commands

from bw.embeds import (
    failed_to_reach_bw_backend,
    failed_to_reach_discord,
    no_group_with_name,
    already_apart_of_group,
    could_not_join_group,
    successfully_joined_group,
)
from bw.interface import User as UserInterface, UserClient
from bw.error import CannotReachBwBackend, CannotReachDiscord, ResponseError
from bw.commands.utils import get_session, groups_autocomplete

logger = logging.getLogger('bw.potbot.command')


class User(commands.Cog, name='User'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='join', description='Join a group')
    @app_commands.autocomplete(group=groups_autocomplete)
    @app_commands.describe(group='The group you want to join.')
    async def join(self, interaction: discord.Interaction, group: str):
        logger.debug('Getting BW session')
        interaction.response.defer()
        try:
            bw_session, oauth_session = await get_session(interaction.followup, interaction.user)
        except CannotReachBwBackend as e:
            logger.error(e)
            await interaction.followup.send(embed=failed_to_reach_bw_backend(), ephemeral=True)
            return
        except CannotReachDiscord as e:
            logger.error(e)
            await interaction.followup.send(embed=failed_to_reach_discord(), ephemeral=True)
            return

        interface = UserInterface(UserClient(bw_session=bw_session, oauth_session=oauth_session))
        try:
            await interface.join_group(group)
            await interaction.followup.send(embed=successfully_joined_group(group), ephemeral=True)
        except ResponseError as err:
            if err.exception.status == 404:
                await interaction.followup.send(embed=no_group_with_name(group), ephemeral=True)
            elif err.exception.status == 409:
                await interaction.followup.send(embed=already_apart_of_group(group), ephemeral=True)
            else:
                await interaction.followup.send(embed=could_not_join_group(group), ephemeral=True)
