from bw.session.types import DiscordSnowflake
from bw.missions.types import MissionUuid
from bw.state import State
from bw.arma.api import ArmaApi
import aiohttp
import discord
import logging
import io
import re
from discord import app_commands
from discord.ext import commands
from bs4 import BeautifulSoup
from uuid import UUID
from typing import Any

from bw.settings import GLOBAL_CONFIGURATION
from bw.environment import ENVIRONMENT
from bw.embeds import (
    modlist_html,
    modlist_website,
    upcoming_session,
    safe_start_ended,
    mission_ended,
    safe_start_ended_basic,
    mission_ended_basic,
)
from bw.events.broker import global_event_broker
from bw.events.decoder import ServerSentEvent
from bw.interface import User

logger = logging.getLogger('bw.potbot.command')


class Community(commands.Cog, name='Community'):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        global_event_broker.add_handler(self.session_event_handler, namespace='session', event=None)

    @app_commands.command(name='html', description='Get the latest version of the BW Modlist HTML')
    async def html(self, interaction: discord.Interaction):
        html_url = GLOBAL_CONFIGURATION.require('html_url').get()
        assert isinstance(html_url, str)

        logger.info(f'{interaction.user} requested the HTML modlist')
        async with aiohttp.ClientSession() as session:
            logger.info(f'Fetching HTML modlist from {html_url}')
            async with session.get(html_url) as response:
                if response.status != 200:
                    logger.error(f'Failed to fetch HTML modlist: {response.status}')
                    await interaction.response.send_message(embed=modlist_website(), ephemeral=False)
                    return
                html = await response.text()
                logger.info('HTML modlist fetched successfully')

        soup = BeautifulSoup(html, 'html.parser')
        logger.info('HTML modlist fetched successfully, attempting to find XML')

        modlist_name = ''
        assert soup.head is not None
        if soup.head.find('script') is None:
            logger.warning('No script tag found in HTML, using default modlist name')
        else:
            script = ''
            for possible_script in soup.head.find_all('script'):
                if len(possible_script.contents) > 0:
                    script = str(possible_script.contents[0])
                    break
            modlist_match = re.search('MOD_LIST_FILE ?= ?"(.*)"', script)
            if modlist_match is None or len(modlist_match.groups()) == 0:
                logger.warning('No modlist name found in HTML, using default name')
                logger.debug(f'script={script}, match={modlist_match}')
                if modlist_match is not None:
                    logger.debug(f'groups={modlist_match.groups()}')
            else:
                modlist_name = modlist_match[1]

        if modlist_name == '':
            logger.error('Failed to fetch modlist filename')
            await interaction.response.send_message(embed=modlist_website(), ephemeral=False)
            return

        logger.debug(f'Fetching XML modlist at "/{modlist_name}"')
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{html_url}/{modlist_name}') as response:
                if response.status != 200:
                    logger.error(f'Failed to fetch XML modlist: {response.status}')
                    await interaction.response.send_message(embed=modlist_website(), ephemeral=False)
                    return
                xml = await response.text()
                logger.info('XML modlist fetched successfully')

        logger.debug(f'Found modlist "{modlist_name}"={len(xml)}')
        modlist = io.BytesIO(xml.encode('utf-8'))
        file = discord.File(modlist, filename=modlist_name)

        await interaction.response.send_message(embed=modlist_html(), file=file, ephemeral=False)

    async def post_session_notification(self, event: ServerSentEvent):
        arma_channel = self.bot.get_channel(ENVIRONMENT.arma_channel_id())
        guild = arma_channel.guild
        roles_to_ping = [guild.get_role(ENVIRONMENT.member_role()), guild.get_role(ENVIRONMENT.recruit_role())]

        message: discord.Message = await arma_channel.send(embed=upcoming_session(roles_to_ping))
        emoji_to_attach: str | discord.Emoji = '🔔'
        for emoji in self.bot.emojis:
            if emoji.name == ENVIRONMENT.session_reminder_emoji_name():
                emoji_to_attach = emoji
                break
        await message.add_reaction(emoji_to_attach)

        session_id = UUID(hex=event.data['session'])
        logger.info(f'Posting session notification to channel [{arma_channel.id}] with session [{session_id}]')

        ArmaApi().create_session_message(State.state, session_id, DiscordSnowflake(message.id))

    async def post_safe_start_ended(self, event: ServerSentEvent):
        channels_to_post = [
            self.bot.get_channel(ENVIRONMENT.arma_channel_id()),
            self.bot.get_channel(ENVIRONMENT.tech_channel_id()),
        ]

        mission_id = UUID(hex=event.data['mission'])
        session_id = UUID(hex=event.data['session'])

        orbat: dict[str, Any] = event.data['orbat']

        logger.info(f'Posting safe-start ending notification for mission [{mission_id}] in session [{session_id}]')

        try:
            mission_information = await User(State.state.api_client).mission_information(MissionUuid(mission_id))
        except Exception as err:
            logger.info(f'Unknown mission or iteration, posting basic info: {err}')
            for channel in channels_to_post:
                await channel.send(embed=safe_start_ended_basic(orbat))
            raise

        for channel in channels_to_post:
            await channel.send(embed=safe_start_ended(mission_information, orbat))

    async def post_mission_end(self, event: ServerSentEvent):
        channels_to_post = [
            self.bot.get_channel(ENVIRONMENT.arma_channel_id()),
            self.bot.get_channel(ENVIRONMENT.tech_channel_id()),
        ]

        async def notify_mission_end(message: str):
            arma_channel: discord.TextChannel = self.bot.get_channel(ENVIRONMENT.arma_channel_id())
            notify_message: discord.Message = await arma_channel.fetch_message(
                int(ArmaApi().session_notification_message(State.state, session_id))
            )
            reacted: set[str] = set()
            for reaction in notify_message.reactions:
                async for user in reaction.users():
                    reacted.add(user.mention)
            await arma_channel.send(f'{message} {" ".join(reacted)}')

        mission_id = UUID(hex=event.data['mission'])
        session_id = UUID(hex=event.data['session'])
        logger.info(f'Posting mission end message for mission [{mission_id}] in session [{session_id}]')

        try:
            mission_information = await User(State.state.api_client).mission_information(MissionUuid(mission_id))
        except Exception as err:
            logger.info(f'Unknown mission, posting basic info: {err}')
            for channel in channels_to_post:
                await channel.send(embed=mission_ended_basic(event.data['starting_orbat'], event.data['final_orbat']))

            await notify_mission_end(
                "A mission has ended! I don't know if its a TvT or Co-op, so everyone is being pinged just in case."
            )
            raise

        for channel in channels_to_post:
            await channel.send(embed=mission_ended(mission_information, event.data['starting_orbat'], event.data['final_orbat']))

        if mission_information.mission_type.tag.is_coop():
            ArmaApi().inform_coop_played(State.state, session_id)
        elif mission_information.mission_type.tag.is_tvt() and not ArmaApi().has_coop_been_played(State.state, session_id):
            # Only post if we ended a TVT and a coop has not been played yet
            # We have an unhandled edge case where is seeding gets > 15 players AND its marked as a coop, we will think that
            # the main Co-op has already ended and we will notify people at TVT slotting
            # If this occurs we will fix it, until then though...
            await notify_mission_end('The TvT has ended, Co-Op slotting is starting soon!')

    async def session_event_handler(self, event: ServerSentEvent) -> None:
        if event.event == 'started':
            await self.post_session_notification(event)
        elif event.event == 'safestart off':
            await self.post_safe_start_ended(event)
        elif event.event == 'finished mission':
            await self.post_mission_end(event)
        else:
            logger.warning(f'No handler defined for event "{event.event}"')
