import datetime
import logging
import re
import shutil
import tempfile
import time
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import Any

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


class UpdateButton(ui.Button):
    def __init__(self, workshop_id: str, channel: discord.TextChannel, parent_view: ui.LayoutView):
        super().__init__(style=discord.ButtonStyle.green, label='Update Mod')
        self.workshop_id = workshop_id
        self.channel = channel
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        logger.debug('Getting BW session')
        await interaction.response.defer(ephemeral=False, thinking=True)
        webhook = interaction.followup
        try:
            bw_session, oauth_session = await get_session(webhook, interaction.user)
        except CannotReachBwBackend as e:
            logger.error(e)
            await webhook.send(
                f'❌ {interaction.user.mention} the mod could not be updated.', embed=failed_to_reach_bw_backend(), ephemeral=True
            )
            return
        except CannotReachDiscord as e:
            logger.error(e)
            await webhook.send(
                f'❌ {interaction.user.mention} the mod could not be updated.', embed=failed_to_reach_discord(), ephemeral=True
            )
            return

        logger.info(f'User {interaction.user.id} is updating {self.workshop_id}')
        interface = User(UserClient(bw_session=bw_session, oauth_session=oauth_session))
        try:
            await interface.update_arma_mod_by_id(int(self.workshop_id))
        except CannotReachBwBackend as e:
            logger.error(f'Failed to update mod on server: {e}')
            await webhook.send(f'❌ {interaction.user.mention} the mod could not be updated.', embed=failed_to_reach_bw_backend())
            return
        except ResponseError as e:
            await webhook.send(f'❌ {interaction.user.mention} the mod could not be updated: {e}')
            return

        self.disabled = True
        await interaction.edit_original_response(view=self.parent_view)


class UpdateModView(ui.LayoutView):
    def __init__(self, *, channel: discord.TextChannel, mod: dict[str, Any]):
        super().__init__()

        def bytes_to_human(bytes: int) -> str:
            byte_threshold = 500
            kilobyte_threshold = 10**3
            megabyte_threshold = 9 * kilobyte_threshold * 100
            gigabyte_threshold = megabyte_threshold * 1000
            if bytes <= byte_threshold:
                return f'{bytes} bytes'
            elif bytes < megabyte_threshold:
                return f'{bytes / 10**3:.2f} kilobytes'
            elif bytes < gigabyte_threshold:
                return f'{bytes / 10**6:.2f} megabytes'
            else:
                return f'{bytes / 10**9:.2f} gigabytes'

        name = mod['title']
        workshop_id = mod['workshop_id']
        preview_url = mod['preview_url']
        bytes = int(mod['file_size_bytes'])

        self.text = ui.TextDisplay(
            f'## **{name}** has updated.\nhttps://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}\n(**{bytes_to_human(bytes)}**)'
        )

        self.preview = discord.MediaGalleryItem(media=preview_url)
        self.gallery = ui.MediaGallery(self.preview)

        self.description = ui.Container()

        self.update = UpdateButton(workshop_id, channel, self)
        self.buttons = ui.ActionRow(self.update)

        container = ui.Container(self.text, self.gallery, ui.Separator(), self.buttons)
        self.add_item(container)
