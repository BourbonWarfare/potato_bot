import discord
import logging
from discord import app_commands
from discord.ext import commands

from bw.embeds import get_bwmf

logger = logging.getLogger('bw.potbot.command')


class MissionMaking(commands.Cog, name='Mission Making'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='bwmf', description='Download the latest Mission Framework')
    async def get_bwmf(self, interaction: discord.Interaction):
        logger.info(f'{interaction.user} requested the BWMF download link.')
        await interaction.response.send_message(embed=get_bwmf(), ephemeral=True)
