import logging

import discord
from discord import ForumChannel, Thread, app_commands
from discord.ext import commands

from bw.commands.modals.mission_making import MissionUploadModal
from bw.discord.api import DiscordApi
from bw.embeds import cannot_upload_no_servers, get_bwmf
from bw.embeds import iteration_information as iteration_information_embed
from bw.environment import ENVIRONMENT
from bw.error import MisconfiguredForumChannel, NoServersToUploadTo
from bw.events.broker import global_event_broker
from bw.events.decoder import ServerSentEvent
from bw.interface import User
from bw.missions.types import IterationUuid
from bw.state import State

logger = logging.getLogger('bw.potbot.command')


class MissionMaking(commands.Cog, name='Mission Making'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        global_event_broker.add_handler(self.mission_event_handler, namespace='mission', event=None)

    @app_commands.command(name='bwmf', description='Download the latest Mission Framework')
    async def get_bwmf(self, interaction: discord.Interaction):
        logger.info(f'{interaction.user} requested the BWMF download link.')
        await interaction.response.send_message(embed=get_bwmf())

    @app_commands.command(name='upload', description='Upload a mission to the selected server')
    async def upload(self, interaction: discord.Interaction):
        try:
            modal = await MissionUploadModal.new()
        except NoServersToUploadTo as e:
            logger.error(f'{interaction.user} cannot upload a mission: {e}')
            await interaction.response.send_message(embed=cannot_upload_no_servers())
        else:
            await interaction.response.send_modal(modal)

    async def mission_event_handler(self, event: ServerSentEvent) -> None:
        channel = self.bot.get_channel(ENVIRONMENT.mission_forum_id())
        if not isinstance(channel, ForumChannel):
            raise MisconfiguredForumChannel(
                f'forum id {type(ENVIRONMENT.mission_forum_id())}({ENVIRONMENT.mission_forum_id()}) = {channel!s}'
            )

        if event.event == 'uploaded':
            iteration_information = await User(State.state.api_client).iteration_information(
                IterationUuid(event.data['iteration'])
            )
            mission_thread = await DiscordApi().get_or_create_mission_thread(State.state, channel, iteration_information)

            forum = self.bot.get_channel(mission_thread.thread_id)
            if not isinstance(forum, Thread):
                raise MisconfiguredForumChannel(f'expected Thread for {mission_thread.thread_id}, got {forum}')

            await forum.send(embed=iteration_information_embed(iteration_information))
        elif event.event == 'reviewed':
            iteration_information = await User(State.state.api_client).iteration_information(
                IterationUuid(event.data['iteration'])
            )
            mission_thread = await DiscordApi().get_or_create_mission_thread(State.state, channel, iteration_information)

            forum = self.bot.get_channel(mission_thread.thread_id)
            if not isinstance(forum, Thread):
                raise MisconfiguredForumChannel(f'expected Thread for {mission_thread.thread_id}, got {forum}')

            await forum.send(f'📝 A new test review was submitted for iteration #{iteration_information.iteration}.')
        elif event.event == 'cosigned':
            # `cosigned` only carries a review uuid; mapping it to an iteration/mission needs a
            # backend lookup we don't have yet. Skip until the db exposes that.
            logger.debug(f'Skipping mission:cosigned event {event.id}: lookup not implemented')
        else:
            logger.debug(f'Ignoring unhandled mission event "{event.event}" ({event.id})')
