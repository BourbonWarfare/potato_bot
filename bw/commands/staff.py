import discord
import logging
from enum import StrEnum
from discord import app_commands
from discord.ext import commands

from bw.embeds import get_bwmf
from bw.error import NoSuchSession
from bw.interface import User
from bw.session.api import SessionApi
from bw.state import State
from bw.commands.authentication import Authentication

logger = logging.getLogger('bw.potbot.command')


class Server(StrEnum):
    MAIN = 'Main Server'
    ALTERNATE = 'Alternate/Offnight Server'
    TRAINING = 'Training Server'
    ALL = 'All Servers'


class Command(StrEnum):
    START = 'Start'
    STOP = 'Stop'
    RESTART = 'Restart'
    UPDATE_GAME = 'Update Server'
    UPDATE_MODS = 'Update Mods'


class Staff(commands.Cog, name='Staff Commands'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='armaserver',
        description='Manage an ARMA server.',
    )
    @app_commands.choices(
        server=[app_commands.Choice(name=choice.value, value=choice.value) for choice in Server],
        option=[app_commands.Choice(name=choice.value, value=choice.value) for choice in Command],
    )
    @app_commands.describe(
        server='The server which to perform the operation on.', option='The operation you wish to perform on the server.'
    )
    async def server_management(self, interaction: discord.Interaction, server: str, option: str):
        server = Server(server)
        option = Command(option)
        logger.info(f'{interaction.user} is performing "{option}" on "{server}"')

        try:
            session = SessionApi().get_bw_session_from_discord_id(State.state, interaction.user.id)
            await interaction.response.defer()
        except NoSuchSession:
            await Authentication(self.bot).internal_login_oauth(interaction)
            session = SessionApi().get_bw_session_from_discord_id(State.state, interaction.user.id)

        if option == Command.START:
            pass
        elif option == Command.STOP:
            pass
        elif option == Command.RESTART:
            pass
        elif option == Command.UPDATE_GAME:
            pass
        elif option == Command.UPDATE_MODS:
            pass
        else:
            raise NotImplementedError()
        await interaction.followup.send(embed=get_bwmf(), ephemeral=True)
