import logging

import discord
from bs4 import BeautifulSoup
from discord import ui

from bw.environment import ENVIRONMENT

logger = logging.getLogger('bw.potbot.command')


class SetTagModal(ui.Modal, title='Set your Arma tag'):
    profile_name = ui.Label(
        text='Profile Name',
        description='The Arma 3 profile name (must be exact)',
        component=ui.TextInput(label='Can be found at'),
    )
    nickname = ui.Label(
        text='Nickname',
        description='Nickname in your entry',
        component=ui.TextInput(required=False),
    )
    steam_id = ui.Label(
        text='Steam ID',
        description='Your Steam64 ID (https://steamid.io/).',
        component=ui.TextInput(),
    )
    remark = ui.Label(
        text='Remark',
        description='A quote or remark displayed on your squad entry',
        component=ui.TextInput(style=discord.TextStyle.paragraph, required=False),
    )

    async def on_submit(self, interaction: discord.Interaction):
        assert isinstance(self.profile_name.component, ui.TextInput)
        assert isinstance(self.nickname.component, ui.TextInput)
        assert isinstance(self.steam_id.component, ui.TextInput)
        assert isinstance(self.remark.component, ui.TextInput)

        profile_name = self.profile_name.component.value
        nickname = self.nickname.component.value
        steam_id = self.steam_id.component.value
        remark = self.remark.component.value

        logger.info(f'Setting tag for {profile_name} {f"({nickname})" if nickname else ""} ({steam_id})')
