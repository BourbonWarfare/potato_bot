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
        logger.debug(f'Found modlist (unencoded) "{modlist}"')
        logger.info('HTML modlist fetched successfully, wrapping and sending')

        modlist_name = 'latest_modlist.html'
        if soup.head.find('script') is None:
            logger.warning('No script tag found in HTML, using default modlist name')
        else:
            script = ''
            for possible_script in soup.head.find_all('script'):
                if len(possible_script.contents) > 0:
                    script = str(possible_script.contents[0])
                    break
            modlist_match = re.search('MOD_LIST_FILE ?= ?"(.*)"', script)
            if modlist_match is None or len(modlist_match.groups()) == 0:
                logger.warning('No modlist name found in HTML, using default name')
                logger.debug(f'script={script}, match={modlist_match}')
                if modlist_match is not None:
                    logger.debug(f'groups={modlist_match.groups()}')
            else:
                modlist_name = modlist_match[1]

        logger.debug(f'Fetching XML modlist at "/{modlist_name}"')
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{html_url}/{modlist_name}') as response:
                if response.status != 200:
                    logger.error(f'Failed to fetch XML modlist: {response.status}')
                    await interaction.response.send_message(embed=modlist_website(), ephemeral=False)
                    return
                xml = await response.text()
                logger.info('XML modlist fetched successfully')

        logger.debug(f'Found modlist "{modlist_name}"={xml}')
        modlist = io.BytesIO(xml.encode('utf-8'))
        file = discord.File(modlist, filename=modlist_name)

        await interaction.response.send_message(embed=modlist_html(), file=file, ephemeral=False)
