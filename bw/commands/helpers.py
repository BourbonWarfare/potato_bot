import discord
import logging
import datetime
import math
from discord import app_commands
from discord.ext import commands

from bw.embeds import docs_website, ping, next_session_time, relative_session_time
from bw.environment import ENVIRONMENT

logger = logging.getLogger('bw.potbot.command')


class Helpers(commands.Cog, name='Helpers'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='docs', description='Get help with the bot')
    async def docs(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=docs_website(),
            ephemeral=True,
        )

    @app_commands.command(name='ping', description='Ping the bot to check if it is online')
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=ping(),
            ephemeral=False,
        )

    @app_commands.command(name='sessiontime', description='Calculate your local time relative to session time')
    @app_commands.describe(offset='Relative time in hours. Can be negative and/or decimal.')
    async def session_time(self, interaction: discord.Interaction, offset: None | float = None):
        WEDNESDAY = 2
        SUNDAY = 6
        LOCAL_SESSION_TIME = ENVIRONMENT.local_session_time()
        hour = LOCAL_SESSION_TIME.seconds // 60 // 60

        today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5)))
        today_weekday = today.weekday()
        if today_weekday == SUNDAY:
            if today > today.replace(hour=hour, minute=0, second=0, microsecond=0):
                # if we are past the session time on Sunday => the next session is Wednesday
                next_session = today + datetime.timedelta(days=3)
            else:
                # Next session is today => later in the day
                next_session = today
        elif today_weekday > WEDNESDAY:
            # Next session is on the next Sunday
            next_session = today + datetime.timedelta(days=(SUNDAY - today_weekday))
        elif today_weekday < WEDNESDAY:
            # Next session is on the next Wednesday
            # Note: we checked if today was sunday already
            next_session = today + datetime.timedelta(days=(WEDNESDAY - today_weekday))
        else:
            if today > today.replace(hour=hour, minute=0, second=0, microsecond=0):
                # If we are past the session time on Wednesday => next session is Sunday
                next_session = today + datetime.timedelta(days=4)
            else:
                # Next session is today => later in the day
                next_session = today
        next_session = next_session.replace(hour=hour, minute=0, second=0, microsecond=0)

        if offset is None:
            await interaction.response.send_message(
                embed=next_session_time(next_session),
                ephemeral=False,
            )
        else:
            hours = math.floor(offset) * 60
            minutes = math.floor((offset - math.floor(offset)) * 60)

            relative_session = next_session + datetime.timedelta(hours=hours, minutes=minutes)

            await interaction.response.send_message(
                embed=relative_session_time(next_session, offset, relative_session),
                ephemeral=False,
            )
