import discord
import logging
import aiohttp
import io
from enum import StrEnum
from discord import app_commands
from discord.ext import commands

from bw import embeds
from bw.error import RefreshFailed, CannotReachBwBackend, CannotReachDiscord
from bw.interface import User, UserClient
from bw.commands.utils import get_session, arma_servers_autocomplete

logger = logging.getLogger('bw.potbot.command')


class ArmaCommand(StrEnum):
    START = 'Start'
    STOP = 'Stop'
    RESTART = 'Restart'


class UpdateChoices(StrEnum):
    MODS = 'Mods'
    SERVER = 'Server'


class Staff(commands.Cog, name='Staff Commands'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='arma',
        description='Manage an ARMA server.',
    )
    @app_commands.autocomplete(server=arma_servers_autocomplete)
    @app_commands.choices(
        option=[app_commands.Choice(name=choice.value, value=choice.value) for choice in ArmaCommand],
    )
    @app_commands.describe(
        server='The server which to perform the operation on.', option='The operation you wish to perform on the server.'
    )
    async def server_management(self, interaction: discord.Interaction, option: str, server: str):
        option = ArmaCommand(option)
        logger.info(f'{interaction.user} is performing "{option}" on "{server}"')

        await interaction.response.defer()
        try:
            bw_session, oauth_session = await get_session(interaction.followup, interaction.user)
        except CannotReachBwBackend as e:
            logger.error(e)
            await interaction.followup.send(embed=embeds.failed_to_reach_bw_backend(), ephemeral=True)
            return
        except CannotReachDiscord as e:
            logger.error(e)
            await interaction.followup.send(embed=embeds.failed_to_reach_discord(), ephemeral=True)
            return

        interface = User(UserClient(oauth_session=oauth_session, bw_session=bw_session))

        async def perform(option: str, server: str) -> dict:
            if option == ArmaCommand.START:
                return await interface.start_arma_server(server)
            elif option == ArmaCommand.STOP:
                return await interface.stop_arma_server(server)
            elif option == ArmaCommand.RESTART:
                return await interface.restart_arma_server(server)
            return {}

        try:
            response = await perform(option=option, server=server)
        except aiohttp.ClientResponseError as e:
            logger.warning(f'User {interaction.user} failed to operate on server: {e}')
            if e.status == 401 or e.status == 403:
                embed = embeds.not_permitted()
            elif e.status == 404:
                embed = embeds.arma_server_not_found(interaction.user, server)
            elif e.status >= 500:
                embed = embeds.server_management_failure(e.message)
            else:
                embed = embeds.failed_arma_server_operation(interaction.user, option, server)
        except RefreshFailed as e:
            logger.error(str(e))
            raise
        except CannotReachBwBackend as e:
            logger.error(f'Failed to operate on server: {e}')
            embed = embeds.failed_to_reach_bw_backend()
        except Exception as e:
            logger.warning(f'Failed to operate on server: {e}')
            embed = embeds.failed_arma_server_operation(interaction.user, option, server)
        else:
            if response.get('startup_status', 'Failed') == 'Failed':
                embed = embeds.failed_arma_server_operation(
                    interaction.user,
                    option,
                    server,
                )
            else:
                embed = embeds.successful_arma_server_operation(
                    interaction.user,
                    option,
                    server,
                    server_status=response.get('server_status', 'Unknown'),
                    hc_status=response.get('hc_status', 'Unknown'),
                    startup_status=response.get('startup_status', 'Unknown'),
                )
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name='serverstatus',
        description='Show the status of an ARMA server.',
    )
    @app_commands.autocomplete(server=arma_servers_autocomplete)
    @app_commands.describe(server='The server which to view the status of.')
    async def get_server_status(self, interaction: discord.Interaction, server: str):
        logger.info(f'{interaction.user} is checking the status of "{server}"')

        await interaction.response.defer()
        try:
            bw_session, oauth_session = await get_session(interaction.followup, interaction.user)
        except CannotReachBwBackend as e:
            logger.error(e)
            await interaction.followup.send(embed=embeds.failed_to_reach_bw_backend(), ephemeral=True)
            return
        except CannotReachDiscord as e:
            logger.error(e)
            await interaction.followup.send(embed=embeds.failed_to_reach_discord(), ephemeral=True)
            return

        interface = User(UserClient(oauth_session=oauth_session, bw_session=bw_session))

        try:
            response = await interface.get_arma_server_status(server)
        except aiohttp.ClientResponseError as e:
            logger.warning(f'User {interaction.user} failed to check server status: {e}')
            if e.status == 401 or e.status == 403:
                embed = embeds.not_permitted()
            elif e.status == 404:
                embed = embeds.arma_server_not_found(interaction.user, server)
            elif e.status >= 500:
                embed = embeds.server_management_failure(e.message)
            else:
                embed = embeds.couldnt_get_arma_server_status(
                    interaction.user,
                    server,
                    server_status=response.get('server_status', 'Unknown'),
                    hc_status=response.get('hc_status', 'Unknown'),
                    startup_status=response.get('startup_status', 'Unknown'),
                )
        except CannotReachBwBackend as e:
            logger.error(f'Failed to operate on server: {e}')
            embed = embeds.failed_to_reach_bw_backend()
        except RefreshFailed as e:
            logger.error(str(e))
            raise e
        except Exception as e:
            logger.warning(f'Failed to operate on server: {e}')
            embed = embeds.couldnt_get_arma_server_status(
                interaction.user,
                server,
                server_status=response.get('server_status', 'Unknown'),
                hc_status=response.get('hc_status', 'Unknown'),
                startup_status=response.get('startup_status', 'Unknown'),
            )
        else:
            result = response.get('result', 'failure')
            if result == 'success':
                embed = embeds.arma_server_status(
                    server,
                    mission=response.get('mission', 'None Selected'),
                    state=response.get('state', 'Unknown'),
                    map=response.get('map', 'None'),
                    players=response.get('players', -1),
                    max_players=response.get('max_players', -1),
                )
            elif result == 'failure':
                embed = embeds.couldnt_get_arma_server_status(
                    interaction.user,
                    server,
                    server_status=response.get('server_status', 'Unknown'),
                    hc_status=response.get('hc_status', 'Unknown'),
                    startup_status=response.get('startup_status', 'Unknown'),
                )
            elif result == 'unresponsive':
                embed = embeds.arma_server_unresponsive(interaction.user, server=server)
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name='update',
        description='Update an ARMA server.',
    )
    @app_commands.autocomplete(server=arma_servers_autocomplete)
    @app_commands.choices(
        update_option=[app_commands.Choice(name=choice.value, value=choice.value) for choice in UpdateChoices],
    )
    @app_commands.describe(
        server='The server which to perform the operation on.', update_option='The operation you wish to perform on the server.'
    )
    async def update_server(self, interaction: discord.Interaction, update_option: str, server: str):
        update_option = UpdateChoices(update_option)
        logger.info(f'{interaction.user} is trying to update {update_option} on "{server}"')

        await interaction.response.defer()
        try:
            bw_session, oauth_session = await get_session(interaction.followup, interaction.user)
        except CannotReachBwBackend as e:
            logger.error(e)
            await interaction.followup.send(embed=embeds.failed_to_reach_bw_backend(), ephemeral=True)
            return
        except CannotReachDiscord as e:
            logger.error(e)
            await interaction.followup.send(embed=embeds.failed_to_reach_discord(), ephemeral=True)
            return

        interface = User(UserClient(oauth_session=oauth_session, bw_session=bw_session))

        async def perform(option: UpdateChoices, server: str) -> dict:
            if option == UpdateChoices.MODS:
                return await interface.update_arma_server_mods(server)
            elif option == UpdateChoices.SERVER:
                return await interface.update_arma_server(server)
            return {}

        embed = None
        try:
            response = await perform(option=update_option, server=server)
        except aiohttp.ClientResponseError as e:
            logger.warning(f'User {interaction.user} failed to update server: {e}')
            if e.status == 401 or e.status == 403:
                embed = embeds.not_permitted()
            elif e.status == 404:
                embed = embeds.arma_server_not_found(interaction.user, server)
            elif e.status >= 500:
                embed = embeds.server_management_failure(e.message)
            else:
                embed = embeds.failed_arma_server_operation(interaction.user, update_option, server)
        except RefreshFailed as e:
            logger.warning(f'{e}. Reattempting whole method...')
            raise
        except CannotReachBwBackend as e:
            logger.error(f'Failed to operate on server: {e}')
            embed = embeds.failed_to_reach_bw_backend()
        except Exception as e:
            logger.warning(f'Failed to operate on server: {e}')
            embed = embeds.failed_arma_server_operation(interaction.user, update_option, server)
        else:
            if update_option == UpdateChoices.MODS:
                servers: dict[str, dict] = response['affected_servers']
                mods: list[dict] = response['updated_mods']
                embed_list = []
                for server_name, server_status in servers.items():
                    embed_list.append(
                        embeds.arma_server_state(
                            server_name,
                            server_status=server_status.get('server_status', 'Unknown'),
                            hc_status=server_status.get('hc_status', 'Unknown'),
                            startup_status=server_status.get('startup_status', 'Unknown'),
                        )
                    )
                mod_update_log = []
                for mod in mods:
                    mod_update_log.append(f'{mod.get("title", "Unknown")}({mod.get("workshop_id", "No Workshop ID")})')
                await interaction.followup.send(f'Mods Updated:\n```{"\n".join(mod_update_log)}```', embeds=embed_list)
            else:
                embed = embeds.successful_server_update(
                    server,
                    server_status=response.get('server_status', 'Unknown'),
                    hc_status=response.get('hc_status', 'Unknown'),
                    startup_status=response.get('startup_status', 'Unknown'),
                )
        finally:
            if embed is not None:
                await interaction.followup.send(embed=embed)

    @app_commands.command(
        name='rpt',
        description='Retrieve RPT file for a server.',
    )
    @app_commands.autocomplete(server=arma_servers_autocomplete)
    @app_commands.describe(server='The server which to retrieve the RPT for.')
    async def get_server_rpt(self, interaction: discord.Interaction, server: str):
        logger.info(f'{interaction.user} is trying to get RPT for "{server}"')

        await interaction.response.defer()
        try:
            bw_session, oauth_session = await get_session(interaction.followup, interaction.user)
        except CannotReachBwBackend as e:
            logger.error(e)
            await interaction.followup.send(embed=embeds.failed_to_reach_bw_backend(), ephemeral=True)
            return
        except CannotReachDiscord as e:
            logger.error(e)
            await interaction.followup.send(embed=embeds.failed_to_reach_discord(), ephemeral=True)
            return

        interface = User(UserClient(oauth_session=oauth_session, bw_session=bw_session))

        embed = None
        try:
            response = await interface.get_arma_server_rpt(server)
        except aiohttp.ClientResponseError as e:
            logger.warning(f'User {interaction.user} failed to update server: {e}')
            if e.status == 401 or e.status == 403:
                embed = embeds.not_permitted()
            elif e.status == 404:
                embed = embeds.arma_server_not_found(interaction.user, server)
            else:
                embed = embeds.failed_to_get_rpt(server, e.message)
        except RefreshFailed as e:
            logger.warning(f'{e}. Reattempting whole method...')
            raise
        except CannotReachBwBackend as e:
            logger.error(f'Failed to operate on server: {e}')
            embed = embeds.failed_to_reach_bw_backend()
        except Exception as e:
            logger.warning(f'Failed to operate on server: {e}')
            embed = embeds.failed_to_get_rpt(server, str(e))
        else:
            rpt_file = io.BytesIO(response.encode('utf-8'))
            await interaction.followup.send(
                f'💬 Latest RPT for {server}', file=discord.File(rpt_file, filename=f'{server}_latest.rpt')
            )
        finally:
            if embed is not None:
                await interaction.followup.send(embed=embed)
