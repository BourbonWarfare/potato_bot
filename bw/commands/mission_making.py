import discord
import logging
import datetime
import tempfile
import time
from zoneinfo import ZoneInfo
from pathlib import Path
from discord import app_commands, ui
from discord.ext import commands

from bw.embeds import get_bwmf
from bw.commands.utils import get_session
from bw.state import State
from bw.interface import User
from bw.error import ResponseError

logger = logging.getLogger('bw.potbot.command')


def server_list() -> list[str]:
    return State.state.arma_server_cache.blocking_servers


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
    server = ui.Label(
        text='Destination Server',
        description='Which server the mission is uploaded to',
        component=ui.Select(
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label=server, value=server, default=(idx == 0)) for idx, server in enumerate(server_list())
            ],
        ),
    )
    footer = ui.TextDisplay(
        '⚠️ Your mission will have some automated tests occur after upload. We will notify you if they succeed or fail.'
    )

    async def on_submit(self, interaction: discord.Interaction):
        assert isinstance(self.mission_file.component, ui.FileUpload)
        assert len(self.mission_file.component.values) == 1
        assert isinstance(self.description.component, ui.TextInput)
        assert isinstance(self.potential_issues.component, ui.TextInput)
        assert isinstance(self.server.component, ui.Select)
        assert isinstance(interaction.channel, discord.TextChannel | discord.Thread)

        server = self.server.component.values[0]
        description = self.description.component.value
        potential_issues = self.potential_issues.component.value

        mission_attachment: discord.Attachment = self.mission_file.component.values[0]
        filename = mission_attachment.filename

        logger.debug('Getting BW session')
        bw_session, oauth_session = await get_session(interaction.followup, interaction.user)
        interface = User(bw_session=bw_session, oauth_session=oauth_session)

        if isinstance(interaction.channel, discord.Thread):
            logger.debug('Retrieving thread')
            await interaction.response.defer(thinking=True)
            thread = interaction.channel
            await thread.send(f'`{filename}` is being uploaded to {server}')
        else:
            logger.debug('Creating thread')
            send_message_response = await interaction.response.send_message(f'`{filename}` is being uploaded to {server}')
            response_message = send_message_response.resource
            assert isinstance(response_message, discord.InteractionMessage)
            thread = await response_message.create_thread(name='Test Log')

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
                        await thread.send(f'Message from server: {e.body}')
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

        await interaction.followup.send(f'✅ {interaction.user.mention} your mission has been uploaded successfully!')


class MissionMaking(commands.Cog, name='Mission Making'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='bwmf', description='Download the latest Mission Framework')
    async def get_bwmf(self, interaction: discord.Interaction):
        logger.info(f'{interaction.user} requested the BWMF download link.')
        await interaction.response.send_message(embed=get_bwmf())

    @app_commands.command(name='upload', description='Upload a mission to the selected server')
    async def upload(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MissionUploadModal())
