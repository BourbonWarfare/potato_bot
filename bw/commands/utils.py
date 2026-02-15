import discord
import logging

from bw.state import State
from bw.error import DiscordSessionExpired, NoSuchSession, RefreshFailed, BwSessionExpired, CannotLogin
from bw.session.oauth import BwSession, OAuthSession
from bw.session.api import SessionApi
from bw.commands.authentication import Authentication

logger = logging.getLogger('bw.potbot.command')

async def get_session(interaction: discord.Interaction) -> tuple[BwSession, OAuthSession]:
    async def show_login() -> tuple[BwSession, OAuthSession]:
        oauth_session = await Authentication(interaction).internal_login_oauth(interaction)
        bw_session = SessionApi().get_bw_session_from_discord_id(State.state, interaction.user.id)
        return bw_session, oauth_session

    try:
        logger.info(f'Loading session for {interaction.user}')
        oauth_session = SessionApi().get_discord_session_from_discord_id(State.state, interaction.user.id)
        if oauth_session.is_expired():
            raise DiscordSessionExpired()

        bw_session = SessionApi().get_bw_session_from_discord_id(State.state, interaction.user.id)
        if bw_session.is_expired():
            raise BwSessionExpired()
    except NoSuchSession:
        logger.info(f'Session invalid for {interaction.user}, creating new one')
        bw_session, oauth_session = await show_login()
    except DiscordSessionExpired:
        logger.info(f'Discord Session expired for {interaction.user}, attempting to refresh')
        try:
            oauth_session = await SessionApi().refresh_oauth_session(State.state, oauth_session)
            bw_session = await SessionApi().login_to_backend(State.state, oauth_session)
        except (RefreshFailed, CannotLogin) as e:
            logger.info(f'Could not refresh session: {e}. Re-logging in')
            SessionApi().revoke_user_session(State.state, interaction.user.id)
            bw_session, oauth_session = await show_login()
    except BwSessionExpired:
        logger.info(f'BW Session expired for {interaction.user}, attemptign to re-login')
        oauth_session = SessionApi().get_discord_session_from_discord_id(State.state, interaction.user.id)
        try:
            bw_session = await SessionApi().login_to_backend(State.state, oauth_session)
        except CannotLogin:
            logger.warning('Cannot login, retrying login')
            SessionApi().revoke_user_session(State.state, interaction.user.id)
            bw_session, oauth_session = await show_login()
    else:
        await interaction.response.defer()
    
    return bw_session, oauth_session