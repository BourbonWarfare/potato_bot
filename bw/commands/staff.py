import discord
import logging
from enum import StrEnum
from discord import app_commands
from discord.ext import commands

from bw.embeds import get_bwmf
from bw.interface import Interface

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
    UPDATE = 'Update'
    MOD_UPDATE = 'Update Mods'


def server_operation(command: Command, server: str):
    if command == Command.START:
        return Interface().start_arma_server(server)


class Staff(commands.Cog, name='Staff Commands'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='armaserver',
        description='Manage an ARMA server.',
    )
    @app_commands.autocomplete(
        server=lambda _, current: [
            app_commands.Choice(name=choice.value, value=choice) for choice in Server if current.lower() in choice.value.lower()
        ],
        option=lambda _, current: [
            app_commands.Choice(name=choice.value, value=choice) for choice in Command if current.lower() in choice.value.lower()
        ],
    )
    @app_commands.choices(
        server=[app_commands.Choice(name=choice.value, value=choice) for choice in Server],
        option=[app_commands.Choice(name=choice.value, value=choice) for choice in Command],
    )
    @app_commands.describe(
        server='The server which to perform the operation on.', option='The operation you wish to perform on the server.'
    )
    async def server_management(self, interaction: discord.Interaction, server: Server, option: Command):
        logger.info(f'{interaction.user} is performing "{option}" on "{server}"')
        if server == Server.ALL:
            results = []
            for server in Server:
                if server == Server.ALL:
                    continue
                results.append(server_operation(option, server.value))
            return results
        else:
            return server_operation(option, server.value)
