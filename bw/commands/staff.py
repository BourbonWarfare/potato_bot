import discord
import logging
from enum import StrEnum
from discord import app_commands
from discord.ext import commands

from bw import embeds
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
            logger.info(f'Loading session for {interaction.user}')
            bw_session = SessionApi().get_bw_session_from_discord_id(State.state, interaction.user.id)
            oauth_session = SessionApi().get_discord_session_from_discord_id(State.state, interaction.user.id)
            await interaction.response.defer()
        except NoSuchSession:
            logger.info(f'No session found for {interaction.user}, creating new one')
            oauth_session = await Authentication(self.bot).internal_login_oauth(interaction)
            bw_session = SessionApi().get_bw_session_from_discord_id(State.state, interaction.user.id)

        interface = User(oauth_session, bw_session)

        async def perform(option: str, server: str) -> bool:
            if option == Command.START:
                return await interface.start_arma_server(server)
            elif option == Command.STOP:
                return await interface.stop_arma_server(server)
            elif option == Command.RESTART:
                return await interface.restart_arma_server(server)
            elif option == Command.UPDATE_GAME:
                return await interface.update_arma_server(server)
            elif option == Command.UPDATE_MODS:
                return await interface.update_arma_server_mods(server)
            return False

        if perform(option=option, server=server):
            embed = embeds.successful_arma_server_operation(interaction.user, option, server)
        else:
            embed = embeds.failed_arma_server_operation(interaction.user, option, server)
        await interaction.followup.send(embed=embed)
