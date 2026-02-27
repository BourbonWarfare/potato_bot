import discord
import logging
import datetime
import tempfile
import time
import io
from zoneinfo import ZoneInfo
from discord import app_commands, ui
from discord.ext import commands

from bw.embeds import get_bwmf
from bw.commands.utils import get_session
from bw.state import State
from bw.interface import User

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
                discord.SelectOption(label=server, value=server, default=(idx == 0))
                for idx, server in enumerate(server_list())
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
        logger.info(
            f'{self.description.component.value}\n{self.potential_issues.component.value}\n{self.server.component.values[0]}'
        )

        mission_attachment: discord.Attachment = self.mission_file.component.values[0]
        filename = mission_attachment.filename

        if isinstance(interaction.channel, discord.Thread):
            logger.debug('Retrieving thread')
            await interaction.response.defer(thinking=True)
            thread = interaction.channel
        else:
            logger.debug('Creating thread')
            send_message_response = await interaction.response.send_message(f'`{filename}` upload information')
            response_message = send_message_response.resource
            assert isinstance(response_message, discord.InteractionMessage)
            thread = await response_message.create_thread(name='Test Log')

        logger.debug('Sending to thread')
        today = datetime.datetime.now(tz=ZoneInfo('America/Chicago'))
        thread.send(f'Mission Uploaded on {today.isoformat('-', 'minutes')}')

        logger.debug('Getting BW session')
        bw_session, oauth_session = await get_session(interaction.followup, interaction.user)
        interface = User(bw_session=bw_session, oauth_session=oauth_session)

        logger.debug('Downloading mission')
        download_t0 = time.time()
        with tempfile.NamedTemporaryFile(mode="wb") as file:
            await self.mission_file.component.values[0].save(file)
        thread.send(f'Mission downloaded (took {time.time() - download_t0:.2f} seconds)')

        interaction.followup.send(f'✅ {interaction.user.mention} your mission has been uploaded successfully!')


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
