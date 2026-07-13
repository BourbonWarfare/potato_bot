from bw.session.types import DiscordSnowflake
import discord
import time
import logging
from discord import app_commands

from bw.state import State
from bw.error import DiscordSessionExpired, NoSuchSession, RefreshFailed, BwSessionExpired, CannotLogin
from bw.session.oauth import BwSession, OAuthSession
from bw.session.api import SessionApi
from bw.commands.authentication import Authentication
from bw.utils import levenshtein_distance

logger = logging.getLogger('bw.potbot.command')


async def get_session(followup: discord.Webhook, user: discord.User | discord.Member) -> tuple[BwSession, OAuthSession]:
    user_id = DiscordSnowflake(user.id)

    async def show_login() -> tuple[BwSession, OAuthSession]:
        oauth_session = await Authentication(None).internal_login_oauth(followup, user_id)
        bw_session = SessionApi().get_bw_session_from_discord_id(State.state, user_id)
        return bw_session, oauth_session

    try:
        logger.info(f'Loading session for {user}')
        oauth_session = SessionApi().get_discord_session_from_discord_id(State.state, user_id)
        if oauth_session.is_expired():
            raise DiscordSessionExpired()

        bw_session = SessionApi().get_bw_session_from_discord_id(State.state, user_id)
        if bw_session.is_expired():
            raise BwSessionExpired()
    except NoSuchSession:
        logger.info(f'Session invalid for {user}, creating new one')
        bw_session, oauth_session = await show_login()
    except DiscordSessionExpired:
        logger.info(f'Discord Session expired for {user}, attempting to refresh')
        try:
            oauth_session = await SessionApi().refresh_oauth_session(State.state, oauth_session)
            bw_session = await SessionApi().login_to_backend(State.state, oauth_session)
        except (RefreshFailed, CannotLogin) as e:
            logger.info(f'Could not refresh session: {e}. Re-logging in')
            SessionApi().revoke_user_session(State.state, user_id)
            bw_session, oauth_session = await show_login()
    except BwSessionExpired:
        logger.info(f'BW Session expired for {user}, attemptign to re-login')
        oauth_session = SessionApi().get_discord_session_from_discord_id(State.state, user_id)
        try:
            bw_session = await SessionApi().login_to_backend(State.state, oauth_session)
        except CannotLogin:
            logger.warning('Cannot login, retrying login')
            SessionApi().revoke_user_session(State.state, user_id)
            bw_session, oauth_session = await show_login()

    return bw_session, oauth_session


async def arma_servers_autocomplete(_, current: str) -> list[app_commands.Choice[str]]:
    async with State.state.arma_server_cache.servers as servers:
        logger.debug('Starting autocomplete')
        start_time = time.time()
        if len(servers) == 0:
            logger.error('Could not find any configured servers')
            return []

        servers_with_distances = sorted(
            [(server, levenshtein_distance(current, server)) for server in servers], key=lambda a: a[1]
        )
        logger.debug(f'{servers_with_distances}')
        logger.debug(f'Autocomplete took {(time.time() - start_time):.4f} seconds')
        return [app_commands.Choice(name=server, value=server) for server, _ in servers_with_distances][:3]


async def groups_autocomplete(_, current: str) -> list[app_commands.Choice[str]]:
    async with State.state.group_cache.groups as groups:
        logger.debug('Starting autocomplete')
        start_time = time.time()
        if len(groups) == 0:
            logger.error('Could not find any configured groups')
            return []

        groups_with_distances = sorted([(group, levenshtein_distance(current, group)) for group in groups], key=lambda a: a[1])
        logger.debug(f'{groups_with_distances}')
        logger.debug(f'Autocomplete took {(time.time() - start_time):.4f} seconds')
        return [app_commands.Choice(name=group, value=group) for group, _ in groups_with_distances][:3]
