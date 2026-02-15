import discord
import logging
import aiohttp
from enum import StrEnum
from discord import app_commands
from discord.ext import commands

from bw import embeds
from bw.utils import levenshtein_distance
from bw.error import RefreshFailed
from bw.interface import Interface, User
from bw.session.api import SessionApi
from bw.state import State
from bw.commands.utils import get_session

logger = logging.getLogger('bw.potbot.command')

async def arma_servers_autocomplete(_, current: str) -> list[app_commands.Choice[str]]:
    try:
        servers = await Interface().get_arma_servers()
    except aiohttp.ClientResponseError as e:
        logger.warning(f'Could not get arma servers: {e}')
        return []

    if len(servers) == 0:
        logger.warning('Could not find any configured servers')
        return []

    servers_with_distances = sorted(
        [(server, levenshtein_distance(current, server)) for server in servers],
        key=lambda a: a[1]
    )
    logger.debug(f'{servers_with_distances}')
    return [app_commands.Choice(name=server, value=server) for server, _ in servers_with_distances][:3]

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
    @app_commands.autocomplete(server=arma_servers_autocomplete)
    @app_commands.choices(
        option=[app_commands.Choice(name=choice.value, value=choice.value) for choice in Command],
    )
    @app_commands.describe(
        server='The server which to perform the operation on.', option='The operation you wish to perform on the server.'
    )
    async def server_management(self, interaction: discord.Interaction, server: str, option: str):
        option = Command(option)
        logger.info(f'{interaction.user} is performing "{option}" on "{server}"')

        bw_session, oauth_session = await get_session(interaction)

        interface = User(oauth_session=oauth_session, bw_session=bw_session)

        async def perform(option: str, server: str) -> dict:
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
            return {}

        try:
            response = await perform(option=option, server=server)
            if await perform(option=option, server=server):
                embed = embeds.successful_arma_server_operation(
                    interaction.user,
                    option,
                    server,
                    server_status=response.get('server_status', 'Unknown'),
                    hc_status=response.get('hc_status', 'Unknown'),
                    startup_status=response.get('startup_status', 'Unknown'),
                )
            else:
                embed = embeds.failed_arma_server_operation(interaction.user, option, server)
        except aiohttp.ClientResponseError as e:
            logger.warning(f'User {interaction.user} failed to operate on server: {e}')
            if e.status == 401 or e.status == 403:
                embed = embeds.not_permitted()
            elif e.status == 404:
                embed = embeds.arma_server_not_found(interaction.user, option, server)
            elif e.status >= 500:
                embed = embeds.backend_failure()
            else:
                embed = embeds.failed_arma_server_operation(interaction.user, option, server)
        except RefreshFailed as e:
            logger.warning(f'{e}. Reattempting whole method...')
            SessionApi().revoke_user_session(State.state, interaction.user.id)
            self.server_management(interaction=interaction, server=server, option=option)
            return
        except Exception as e:
            logger.warning(f'Failed to operate on server: {e}')
            embed = embeds.failed_arma_server_operation(interaction.user, option, server)
        await interaction.followup.send(embed=embed)
