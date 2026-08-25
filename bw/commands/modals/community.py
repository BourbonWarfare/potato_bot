from bw.environment import ENVIRONMENT
from bs4 import BeautifulSoup
import logging

import discord
from discord import ui

logger = logging.getLogger('bw.potbot.command')


class SetTagModal(ui.Modal, title='Set your Arma tag'):
    name = ui.Label(
        text='Profile Name',
        description='The Arma 3 display name (must be exact)',
        component=ui.TextInput(label='Can be found at'),
    )
    nickname = ui.Label(
        text='Nickname',
        description='What name you want displayed in your squad entry',
        component=ui.TextInput(label='Only if you want something displayed other than your Arma profile name'),
    )
    steam_id = ui.Label(
        text='Steam ID',
        description='Your Steam64 ID.',
        component=ui.TextInput(label='Can be found at https://steamid.io/'),
    )
    remark = ui.Label(
        text='Remark',
        description='A quote or remark displayed on your squad entry',
        component=ui.TextInput(style=discord.TextStyle.paragraph, required=False),
    )

    async def on_submit(self, interaction: discord.Interaction):
        assert isinstance(self.name.component, ui.TextInput)
        assert isinstance(self.nickname.component, ui.TextInput)
        assert isinstance(self.steam_id.component, ui.TextInput)
        assert isinstance(self.remark.component, ui.TextInput)

        name = self.name.component.value
        nickname = self.nickname.component.value
        steam_id = self.steam_id.component.value
        remark = self.remark.component.value

        logger.info(f'Setting tag for {name} ({steam_id})')
        with open(ENVIRONMENT.squad_xml_filepath()) as file:
            soup = BeautifulSoup(file.read())
