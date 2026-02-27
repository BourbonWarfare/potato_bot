import discord
import logging
from discord import app_commands
from discord.ext import commands

from bw.embeds import get_bwmf
from bw.commands.utils import get_session, arma_servers_autocomplete

logger = logging.getLogger('bw.potbot.command')


class MissionMaking(commands.Cog, name='Mission Making'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='bwmf', description='Download the latest Mission Framework')
    async def get_bwmf(self, interaction: discord.Interaction):
        logger.info(f'{interaction.user} requested the BWMF download link.')
        await interaction.response.send_message(embed=get_bwmf(), ephemeral=True)

    @app_commands.command(name='upload', description='Upload a mission to the selected server')
    @app_commands.autocomplete(server=arma_servers_autocomplete)
    @app_commands.describe(
        server='The server which to upload the mission to',
        mission='The mission to upload'
    )
    async def upload(self, interaction: discord.Interaction, server: str, mission: discord.Attachment):
        interaction.response.send_message('Upload stub')
