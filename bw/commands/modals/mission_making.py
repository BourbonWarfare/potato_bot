import datetime
import logging
import re
import shutil
import tempfile
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import discord
from discord import ui

from bw.commands.utils import get_session
from bw.embeds import failed_to_reach_bw_backend, failed_to_reach_discord
from bw.environment import ENVIRONMENT
from bw.error import CannotReachBwBackend, CannotReachDiscord, NoServersToUploadTo, ResponseError
from bw.interface import User, UserClient
from bw.session.types import DiscordSnowflake
from bw.state import State

logger = logging.getLogger('bw.potbot.command')

NOT_BINARIZED = re.compile('mission needs to be binarized to upload')
NOT_SAVED_WITH_POTATO_REGEX = re.compile('not saved with POTATO')
NO_CUSTOM_ATTRIBUTES = re.compile('missing CustomAttributes')

ALLOW_TO_UPLOAD_FORCE: tuple[re.Pattern, ...] = (NOT_BINARIZED, NOT_SAVED_WITH_POTATO_REGEX, NO_CUSTOM_ATTRIBUTES)

ERROR_TO_HUMAN: tuple[tuple[re.Pattern, str], ...] = (
    (NOT_BINARIZED, 'Missions need to be binarized to be uploaded to the server'),
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
    (
        re.compile('User does not have enough permissions to access this resource'),
        "You don't have permission to upload the mission. Have you `/join`ed the Mission Maker group?.",
    ),
)


def human_upload_error(body: str) -> str:
    for pattern, human_reason in ERROR_TO_HUMAN:
        if pattern.search(body):
            return human_reason
    return f'Message from server: {body}'


def upload_error_allows_force(body: str) -> bool:
    return any(pattern.search(body) for pattern in ALLOW_TO_UPLOAD_FORCE)


class ForceUploadButton(ui.Button):
    def __init__(self, server: str, uploaded_file: Path, thread: discord.Thread):
        super().__init__(style=discord.ButtonStyle.danger, label='Continue Upload')

        self.uploaded_file = uploaded_file
        self.thread = thread
        self.server = server

    async def callback(self, interaction: discord.Interaction):
        logger.debug('Getting BW session')
        try:
            bw_session, oauth_session = await get_session(self.thread, interaction.user)
        except CannotReachBwBackend as e:
            logger.error(e)
            await self.thread.send('❌ Failed to upload: the BW server is not responding')
            await interaction.response.send_message(embed=failed_to_reach_bw_backend(), ephemeral=True)
            return
        except CannotReachDiscord as e:
            logger.error(e)
            await self.thread.send('❌ Failed to upload: we cannot reach Discord for OAuth')
            await interaction.response.send_message(embed=failed_to_reach_discord(), ephemeral=True)
            return

        logger.info('Uploading mission to server by force')
        interface = User(UserClient(bw_session=bw_session, oauth_session=oauth_session))
        try:
            await interface.force_upload_mission(self.uploaded_file, self.server)
        except CannotReachBwBackend as e:
            logger.error(f'Failed to operate on server: {e}')
            await interaction.response.send_message(
                f'❌ {interaction.user.mention} your mission could not be uploaded.', embed=failed_to_reach_bw_backend()
            )
            return
        except ResponseError as e:
            await interaction.response.send_message(
                f'❌ {interaction.user.mention} your mission could not be uploaded regardless.'
            )
            if e.exception.status == 409:
                await self.thread.send('A mission with this filename already exists on this server.')
            elif e.exception.status == 422:
                await self.thread.send('The mission could not be processed.')
            if e.body:
                await self.thread.send(human_upload_error(e.body))
        else:
            await interaction.response.send_message(
                'Mission has been uploaded to the server.\n## This will **not** be played in session'
            )
        finally:
            logger.info(f'Cleaning up forced upload directory {self.uploaded_file.parent}')
            shutil.rmtree(self.uploaded_file.parent, ignore_errors=True)


class UploadOverwriteView(ui.LayoutView):
    def __init__(self, *, uploaded_file: Path, owner: DiscordSnowflake, thread: discord.Thread, server: str):
        super().__init__()

        with tempfile.TemporaryDirectory(delete=False) as directory:
            self.copied_directory = Path(directory)
            new_uploaded_file = self.copied_directory / uploaded_file.name
            shutil.copyfile(uploaded_file, new_uploaded_file)

        self.owner = owner

        self.text = ui.TextDisplay(
            '## This mission is not saved with BWMF.\nYou can continue to upload it, but it will _**not**_ be played in session.'
        )
        self.go_ahead = ForceUploadButton(server, new_uploaded_file, thread)
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
        server_selector: ui.Select | None = None
        for child in self.walk_children():
            if isinstance(child, ui.Label):
                to_check.append(child)
        for label in to_check:
            if isinstance(label.component, ui.Select) and label.component.custom_id == 'server_selector':
                server_selector = label.component
                break

        assert isinstance(self.mission_file.component, ui.FileUpload)
        assert len(self.mission_file.component.values) == 1
        assert isinstance(self.description.component, ui.TextInput)
        assert isinstance(self.potential_issues.component, ui.TextInput)
        if server_selector is None:
            await interaction.response.send_message(
                'Mission cannot be uploaded: no destination server was selected.', ephemeral=True
            )
            return
        assert isinstance(interaction.channel, discord.TextChannel | discord.Thread)

        server = server_selector.values[0]
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
            return

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
                        await thread.send(human_upload_error(e.body))

                        if upload_error_allows_force(e.body):
                            logger.info('Error can allow a forced upload')
                            await thread.send(
                                view=UploadOverwriteView(
                                    server=server,
                                    uploaded_file=temp_file,
                                    owner=DiscordSnowflake(interaction.user.id),
                                    thread=thread,
                                )
                            )

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
