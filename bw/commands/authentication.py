import discord
import logging
import secrets
import aiohttp
import asyncio
from discord import app_commands
from discord.ext import commands

from bw.embeds import login_with_discord, logged_in_with_discord, failed_to_login_with_discord, already_logged_in
from bw.utils import backoff
from bw.interface import Interface
from bw.session.api import SessionApi
from bw.session.types import DiscordSnowflake
from bw.session.oauth import OAuthSession
from bw.state import State
from bw.error import CannotLogin, NoSuchSession

logger = logging.getLogger('bw.potbot.command')


class Authentication(commands.Cog, name='Authentication'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='login',
        description='Login to POTBOT with Discord.',
    )
    async def login_oauth(self, interaction: discord.Interaction):
        try:
            discord_session = SessionApi().get_discord_session_from_discord_id(State.state, DiscordSnowflake(interaction.user.id))
        except NoSuchSession:
            pass
        else:
            if not discord_session.is_expired():
                await interaction.response.send_message(embed=already_logged_in(), ephemeral=True)
                return

        try:
            await self.internal_login_oauth(interaction)
        except CannotLogin as e:
            logger.info(e)
            await interaction.followup.send(embed=failed_to_login_with_discord(), ephemeral=True)
        else:
            logger.info('successfully logged in')
            await interaction.followup.send(embed=logged_in_with_discord(), ephemeral=True)

    async def internal_login_oauth(self, interaction: discord.Interaction) -> OAuthSession:
        logger.info(f'Attempting new login for {interaction.user.id}')
        state = secrets.token_urlsafe(64)[:32]
        logger.info('sending login link')
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.followup.send(embed=login_with_discord(state), ephemeral=True)

        logger.info('waiting for user...')
        await asyncio.sleep(4)

        @backoff(delay=1, retries=10, max_delay=9)
        async def get_code(state: str) -> str:
            logger.info('attempting getting access code')
            return (await Interface().auth_get_access_code(state)).get('access_code')

        try:
            access_code = await get_code(state)
        except aiohttp.ClientResponseError as e:
            raise CannotLogin(e)
        
        logger.info('Starting OAuth session with access code')
        return await SessionApi().start_oauth_session(
            State.state, discord_id=DiscordSnowflake(interaction.user.id), access_code=access_code
        )
