import discord
import logging
from discord import app_commands, ui
from discord.ext import commands

from bw.embeds import get_bwmf
from bw.commands.utils import get_session
from bw.state import State
from bw.interface import User

logger = logging.getLogger('bw.potbot.command')


def server_list() -> list[str]:
    return State.state.arma_server_cache.potentially_uninitialised_servers


class MissionUploadModal(ui.Modal, title='Upload a Mission'):
    mission_file = ui.Label(
        text='Mission File', description='The mission you want to upload', component=ui.FileUpload(min_values=1, required=True)
    )
    description = ui.Label(
        text='Description',
        description='Describe this iteration of the mission',
        component=ui.TextInput(style=discord.TextStyle.long),
    )
    potential_issues = ui.Label(
        text='Potential Issues',
        description='Describe anything which you want to be tested directly',
        component=ui.TextInput(style=discord.TextStyle.long),
    )
    _1 = ui.Separator()
    server = ui.Label(
        text='Destination Server',
        description='Which server the mission is uploaded to',
        component=ui.Select(
            min_values=1,
            max_values=1,
            required=True,
            options=[
                discord.SelectOption(label=server, value=server, default=(idx == 0))
                for idx, server in enumerate(server_list())
            ],
        ),
    )
    footer = ui.TextDisplay(
        'Your mission will have some automated tests occur after upload. We will notify you if they succeed or fail.'
    )

    interface_: User

    async def on_submit(self, interaction: discord.Interaction):
        assert isinstance(self.mission_file.component, ui.FileUpload)
        assert isinstance(self.description.component, ui.TextInput)
        assert isinstance(self.potential_issues.component, ui.TextInput)
        assert isinstance(self.server.component, ui.Select)
        logger.info(
            f'{self.description.component.value}\n{self.potential_issues.component.value}\n{self.server.component.values[0]}'
        )
        bw_session, oauth_session = await get_session(interaction)
        interface = User(bw_session=bw_session, oauth_session=oauth_session)
        interaction.response.send_message('test')


class MissionMaking(commands.Cog, name='Mission Making'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='bwmf', description='Download the latest Mission Framework')
    async def get_bwmf(self, interaction: discord.Interaction):
        logger.info(f'{interaction.user} requested the BWMF download link.')
        await interaction.response.send_message(embed=get_bwmf(), ephemeral=True)

    @app_commands.command(name='upload', description='Upload a mission to the selected server')
    async def upload(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MissionUploadModal())
