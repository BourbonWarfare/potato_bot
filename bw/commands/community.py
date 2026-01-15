import aiohttp
import discord
import logging
import io
import re
from discord import app_commands
from discord.ext import commands
from bs4 import BeautifulSoup

from bw.settings import GLOBAL_CONFIGURATION
from bw.embeds import modlist_html, modlist_website

logger = logging.getLogger('bw.potbot.command')


class Community(commands.Cog, name='Community'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='html', description='Get the latest version of the BW Modlist HTML')
    async def html(self, interaction: discord.Interaction):
        html_url = GLOBAL_CONFIGURATION.require('html_url').get()
        logger.info(f'{interaction.user} requested the HTML modlist')
        async with aiohttp.ClientSession() as session:
            logger.info(f'Fetching HTML modlist from {html_url}')
            async with session.get(html_url) as response:
                if response.status != 200:
                    logger.error(f'Failed to fetch HTML modlist: {response.status}')
                    await interaction.response.send_message(embed=modlist_website(), ephemeral=False)
                    return
                html = await response.text()
                logger.info('HTML modlist fetched successfully')

        soup = BeautifulSoup(html, 'html.parser')
        if soup.find(id='modListContainer') is None:
            logger.error('No modlist container found in HTML')
            await interaction.response.send_message(
                'Cannot fetch modlist due to an error in the HTML structure. Please try again later.',
                embed=modlist_website(),
                ephemeral=False,
            )
            return

        modlist = soup.get('modListContainer')
        logger.info('HTML modlist fetched successfully, wrapping and sending')

        modlist_name = 'latest_modlist.html'
        if soup.head.find('script') is None:
            logger.warning('No script tag found in HTML, using default modlist name')
        else:
            script = ''
            for possible_script in soup.head.find_all('script'):
                if len(possible_script.contents) > 0:
                    script = possible_script.contents[0]
                    break
            modlist_match = re.match('MOD_LIST_FILE ?= ?"(.*)"', script)
            if len(modlist_match.groups()) <= 1:
                logger.warning('No modlist name found in HTML, using default name')
            else:
                modlist_name = modlist_match[1]

        modlist = io.BytesIO(modlist.encode('utf-8'))
        file = discord.File(modlist, filename=modlist_name)

        await interaction.response.send_message(embed=modlist_html(), file=file, ephemeral=False)
