import shutil
from bw.session.types import DiscordSnowflake
from bw.missions.types import IterationUuid
from bw.environment import ENVIRONMENT
from bw.discord.api import DiscordApi
from bw.embeds import iteration_information as iteration_information_embed
from bw.events.decoder import ServerSentEvent
import discord
import logging
import datetime
import tempfile
import time
import re
from zoneinfo import ZoneInfo
from pathlib import Path
from discord import app_commands, ui, ForumChannel, Thread
from discord.ext import commands

from bw.embeds import get_bwmf, failed_to_reach_bw_backend, failed_to_reach_discord, cannot_upload_no_servers
from bw.commands.utils import get_session
from bw.state import State
from bw.interface import User, UserClient
from bw.error import ResponseError, CannotReachBwBackend, CannotReachDiscord, NoServersToUploadTo, MisconfiguredForumChannel
from bw.events.broker import global_event_broker

logger = logging.getLogger('bw.potbot.command')

NOT_SAVED_WITH_POTATO_REGEX = re.compile('not saved with POTATO')
NO_CUSTOM_ATTRIBUTES = re.compile('missing CustomAttributes')

ALLOW_TO_UPLOAD_FORCE: tuple[re.Pattern, ...] = (NOT_SAVED_WITH_POTATO_REGEX, NO_CUSTOM_ATTRIBUTES)

ERROR_TO_HUMAN: tuple[tuple[re.Pattern, str], ...] = (
    (re.compile('mission needs to be binarized to upload'), 'Missions need to be binarized to be uploaded to the server'),
    (re.compile('missing mission type'), 'You have not selected a mission type in the Mission Testing Attributes'),
    (
        NO_CUSTOM_ATTRIBUTES,
        'This is not a BWMF mission',
    ),
    (
        NOT_SAVED_WITH_POTATO_REGEX,
        'You have not saved this mission in the editor with POTATO loaded',
    ),
    (re.compile('Stored mission has no attached map'), 'Uploaded files need to have a map in the filename'),
    (
        re.compile('no mission type with tag "[0-9]+" exists'),
        'You have somehow uploaded a mission without a known mission tag.'
        'Either pick one that exists, or someone needs to update our database.',
    ),
    (
        re.compile('mission cannot be copied since it already exists'),
        'The mission you have uploaded already exists on the server. Rename the file and try again.',
    ),
    (
        re.compile('mission (?:"[a-zA-Z0-9-]+" )?does not exist'),
        'Something went wrong, the mission does not exist in the database. This is probably not your fault, tell the Tech Mods.',
    ),
    (
        re.compile('could not create mission iteration'),
        'This mission iteration already exists. Try again, and if this error does not happen again you have gotten very lucky.',
    ),
)


class ForceUploadButton(ui.Button):
    def __init__(self, uploaded_file: Path, thread: discord.Thread):
        super().__init__(style=discord.ButtonStyle.danger, label='Continue Upload')

        self.uploaded_file = uploaded_file
        self.thread = thread

    async def callback(self, interaction: discord.Interaction):
        logger.debug('Getting BW session')
        interaction.response.defer(ephemeral=True)
        try:
            bw_session, oauth_session = await get_session(interaction.followup, interaction.user)
        except CannotReachBwBackend as e:
            logger.error(e)
            await self.thread.send('❌ Failed to upload: the BW server is not responding')
            await interaction.followup.send(embed=failed_to_reach_bw_backend(), ephemeral=True)
            return
        except CannotReachDiscord as e:
            logger.error(e)
            await self.thread.send('❌ Failed to upload: we cannot reach Discord for OAuth')
            await interaction.followup.send(embed=failed_to_reach_discord(), ephemeral=True)
            return

        logger.info('Uploading mission to server by force')
        interface = User(UserClient(bw_session=bw_session, oauth_session=oauth_session))


class UploadOverwriteView(ui.LayoutView):
    def __init__(self, *, uploaded_file: Path, owner: DiscordSnowflake, thread: discord.Thread):
        super().__init__()

        with tempfile.TemporaryDirectory(delete=False) as directory:
            self.copied_directory = Path(directory)
            new_uploaded_file = self.copied_directory / uploaded_file.name
            shutil.copyfile(uploaded_file, new_uploaded_file)

        self.owner = owner

        self.text = ui.TextDisplay(
            '## This mission is not saved with BWMF.\nYou can continue to upload it, but it will _**not**_ be played in session.'
        )
        self.go_ahead = ForceUploadButton(new_uploaded_file, thread)
        self.buttons = ui.ActionRow(self.go_ahead)

        container = ui.Container(self.text, self.buttons)
        self.add_item(container)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == int(self.owner)

    async def on_timeout(self):
        logger.info(f'Cleaning up directory {self.copied_directory} (view expired)')
        shutil.rmtree(self.copied_directory)


class MissionUploadModal(ui.Modal, title='Upload a Mission'):
    mission_file = ui.Label(
        text='Mission File', description='The mission you want to upload', component=ui.FileUpload(min_values=1)
    )
    description = ui.Label(
        text='Description',
        description='Describe this iteration of the mission',
        component=ui.TextInput(style=discord.TextStyle.paragraph, required=False),
    )
    potential_issues = ui.Label(
        text='Potential Issues',
        description='Describe anything which you want to be tested directly',
        component=ui.TextInput(style=discord.TextStyle.paragraph, required=False),
    )

    @classmethod
    async def new(cls):
        modal = cls()
        async with State.state.arma_server_cache.servers as servers:
            if servers == []:
                raise NoServersToUploadTo()
            modal.add_item(
                ui.Label(
                    text='Destination Server',
                    description='Which server the mission is uploaded to',
                    component=ui.Select(
                        custom_id='server_selector',
                        min_values=1,
                        max_values=1,
                        options=[
                            discord.SelectOption(label=server, value=server, default=(idx == 0))
                            for idx, server in enumerate(servers)
                        ],
                    ),
                )
            )
            modal.add_item(
                ui.TextDisplay(
                    '⚠️ Your mission will have some automated tests occur after upload. '
                    'We will notify you if they succeed or fail.',
                )
            )
        return modal

    async def on_submit(self, interaction: discord.Interaction):
        to_check: list[ui.Label] = []
        for child in self.walk_children():
            if isinstance(child, ui.Label):
                to_check.append(child)
        for label in to_check:
            if isinstance(label.component, ui.Select) and label.component.custom_id == 'server_selector':
                server = label.component
                break

        assert isinstance(self.mission_file.component, ui.FileUpload)
        assert len(self.mission_file.component.values) == 1
        assert isinstance(self.description.component, ui.TextInput)
        assert isinstance(self.potential_issues.component, ui.TextInput)
        assert isinstance(server, ui.Select)
        assert isinstance(interaction.channel, discord.TextChannel | discord.Thread)

        server = server.values[0]
        description = self.description.component.value
        potential_issues = self.potential_issues.component.value

        mission_attachment: discord.Attachment = self.mission_file.component.values[0]
        filename = mission_attachment.filename

        if isinstance(interaction.channel, discord.Thread):
            logger.debug('Retrieving thread')
            thread = interaction.channel
            await thread.send(f'`{filename}` is being uploaded to {server}')
        else:
            logger.debug('Creating thread')
            send_message_response = await interaction.response.send_message(f'`{filename}` is being uploaded to {server}')
            response_message = send_message_response.resource
            assert isinstance(response_message, discord.InteractionMessage)
            thread: discord.Thread = await response_message.create_thread(name='Upload Log')

        logger.debug('Verifying user input')
        max_char_length = 1950
        if len(description) > max_char_length:
            await thread.send(
                'Your wrote too much in the upload description, mission cannot be uploaded.'
                f'({len(description)} / {max_char_length})'
            )
            return
        if len(potential_issues) > 1950:
            await thread.send(
                'Your wrote too much in the potential issues, mission cannot be uploaded.'
                f'({len(potential_issues)} / {max_char_length})'
            )

        logger.debug('Getting BW session')
        try:
            bw_session, oauth_session = await get_session(interaction.followup, interaction.user)
        except CannotReachBwBackend as e:
            logger.error(e)
            await thread.send('❌ Failed to upload: the BW server is not responding')
            await interaction.followup.send(embed=failed_to_reach_bw_backend(), ephemeral=True)
            return
        except CannotReachDiscord as e:
            logger.error(e)
            await thread.send('❌ Failed to upload: we cannot reach Discord for OAuth')
            await interaction.followup.send(embed=failed_to_reach_discord(), ephemeral=True)
            return

        interface = User(UserClient(bw_session=bw_session, oauth_session=oauth_session))

        logger.debug('Sending to thread')
        today = datetime.datetime.now(tz=ZoneInfo('America/Chicago'))
        await thread.send(f'Mission uploaded <t:{int(today.timestamp())}:R>')

        await thread.send(f'Upload Description: {description}')
        await thread.send(f'Potential Issues: {potential_issues}')

        changelog = {'description': description, 'potential_issues': potential_issues}

        logger.debug('Downloading mission')
        download_t0 = time.time()
        with tempfile.TemporaryDirectory() as directory:
            temp_file = Path(directory) / filename
            with open(temp_file, mode='wb') as file:
                await self.mission_file.component.values[0].save(file)
                try:
                    upload_response = await interface.upload_mission(temp_file, server, changelog)
                except CannotReachBwBackend as e:
                    logger.error(f'Failed to operate on server: {e}')
                    await interaction.followup.send(
                        f'❌ {interaction.user.mention} your mission could not be uploaded.', embed=failed_to_reach_bw_backend()
                    )
                    return
                except ResponseError as e:
                    await interaction.followup.send(
                        f'❌ {interaction.user.mention} your mission could not be uploaded. Please check logs for further details'
                    )
                    await thread.send('----- ERROR LOG -----')
                    if e.exception.status == 409:
                        await thread.send('A mission with this filename already exists on this server.')
                    elif e.exception.status == 422:
                        await thread.send('The mission could not be processed.')
                    if e.body:
                        information = f'Message from server: {e.body}'
                        for pattern, human_reason in ERROR_TO_HUMAN:
                            if pattern.search(e.body):
                                information = human_reason
                        await thread.send(information)

                        for pattern in ALLOW_TO_UPLOAD_FORCE:
                            logger.debug(f'Checking "{pattern}" against "{e.body}"')
                            if pattern.search(e.body):
                                logger.info('Error can allow a forced uploaded')
                                await thread.send(
                                    view=UploadOverwriteView(
                                        uploaded_file=temp_file, owner=DiscordSnowflake(interaction.user.id), thread=thread
                                    )
                                )
                                break

                    return
        await thread.send(f'Mission downloaded in {time.time() - download_t0:.2f} second(s)')
        await thread.send(f'Mission iteration #{upload_response.iteration_number}')

        mission_length = upload_response.mission_length
        safe_start_length = upload_response.safe_start_length
        mission_length_format = f'{mission_length // 60:02d}:{mission_length % 60:02d}'
        safe_start_length_format = f'{safe_start_length // 60:02d}:{safe_start_length % 60:02d}'

        await thread.send(rf"""----- ITERATION INFORMATION -----
    Minimum Players: {upload_response.min_players}
    Maximum Players: {upload_response.max_players}
    Desired Players: {upload_response.desired_players}
    Safe Start Length: {safe_start_length_format}
    Mission Length: {mission_length_format}""")

        await interaction.followup.send(
            f'✅ {interaction.user.mention} your mission has been uploaded successfully!'
            f' Please check <#{ENVIRONMENT.mission_forum_id()}> for your mission thread.'
        )


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
                f'forum id {type(ENVIRONMENT.mission_forum_id())}({ENVIRONMENT.mission_forum_id()}) = {str(channel)}'
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
