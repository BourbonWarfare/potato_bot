import logging
from typing import Any, cast

import aiohttp
import discord
from discord import ui

from bw.commands.utils import get_session
from bw.embeds import failed_to_reach_bw_backend, failed_to_reach_discord
from bw.error import CannotReachBwBackend, CannotReachDiscord
from bw.interface import User, UserClient
from bw.session.oauth import BwSession, OAuthSession

logger = logging.getLogger('bw.potbot.command')


class SetTagModal(ui.Modal, title='Set your Arma tag'):
    profile_name = ui.Label(
        text='Profile Name',
        description='The Arma 3 profile name (must be exact)',
        component=ui.TextInput(),
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

    @classmethod
    async def new(cls, bw_session: BwSession, oauth_session: OAuthSession):
        modal = cls()
        assert isinstance(modal.profile_name.component, ui.TextInput)
        assert isinstance(modal.nickname.component, ui.TextInput)
        assert isinstance(modal.steam_id.component, ui.TextInput)
        assert isinstance(modal.remark.component, ui.TextInput)

        interface = User(UserClient(bw_session=bw_session, oauth_session=oauth_session))
        try:
            squad_tag = await interface.get_squad_tag()
        except aiohttp.ClientResponseError:
            squad_tag = {'profile_name': '', 'steam_id': '', 'nickname': '', 'remark': ''}

        cast(Any, modal.profile_name.component).default = str(squad_tag.get('profile_name', ''))
        cast(Any, modal.nickname.component).default = str(squad_tag.get('nickname', ''))
        cast(Any, modal.steam_id.component).default = str(squad_tag.get('steam_id', ''))
        cast(Any, modal.remark.component).default = str(squad_tag.get('remark', ''))

        return modal

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
        await interaction.response.defer(ephemeral=True, thinking=True)

        logger.debug('Getting BW session')
        try:
            bw_session, oauth_session = await get_session(interaction.followup, interaction.user)
        except CannotReachBwBackend as e:
            logger.error(e)
            await interaction.followup.send(embed=failed_to_reach_bw_backend(), ephemeral=True)
            return
        except CannotReachDiscord as e:
            logger.error(e)
            await interaction.followup.send(embed=failed_to_reach_discord(), ephemeral=True)
            return

        interface = User(UserClient(bw_session=bw_session, oauth_session=oauth_session))
        await interface.set_squad_tag(profile_name, nickname, steam_id, remark)
        await interaction.followup.send('Successfully updated squad XML', ephemeral=True)
