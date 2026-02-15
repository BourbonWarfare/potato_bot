import discord
import datetime
import urllib
from bw.environment import ENVIRONMENT


def default() -> discord.Embed:
    return discord.Embed(
        title="Someone hasn't configured something",
        description="This is the default embed that occurs when we don't know what to put yet",
        colour=ENVIRONMENT.embed_colour_member(),
    )


def backend_failure() -> discord.Embed:
    return discord.Embed(
        title="🔨 Something is wrong with the server...",
        description="An error has occured that the bot cannot handle. Please ping techmods.",
        colour=ENVIRONMENT.embed_colour_member(),
    )


def not_permitted() -> discord.Embed:
    return discord.Embed(
        title="❌ You are not allowed to do that",
        description="You have tried to perform an action that you do not have permissions for",
        colour=ENVIRONMENT.embed_colour_member(),
    )


def get_bwmf() -> discord.Embed:
    return discord.Embed(
        title='📂 CLICK HERE to download',
        description='Or visit the [GitHub](https://github.com/BourbonWarfare/bwmf)',
        url='https://github.com/BourbonWarfare/bwmf/archive/refs/heads/master.zip',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def get_generic_handbook() -> discord.Embed:
    return discord.Embed(
        title='📓 CLICK HERE to open handbook',
        description='Handbooks and other useful information can be found on our website: https://docs.bourbonwarfare.com/wiki/.',
        url='https://docs.bourbonwarfare.com/wiki/',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def get_recruit_handbook() -> discord.Embed:
    return discord.Embed(
        title='📓 CLICK HERE to open handbook',
        description='Handbooks and other useful information can be found on our website: https://docs.bourbonwarfare.com/wiki/.',
        url='https://docs.bourbonwarfare.com/wiki/welcome-to-bw/recruit-handbook',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def get_member_handbook() -> discord.Embed:
    return discord.Embed(
        title='📓 CLICK HERE to open handbook',
        description='Handbooks and other useful information can be found on our website: https://docs.bourbonwarfare.com/wiki/.',
        url='https://forums.bourbonwarfare.com/viewtopic.php?t=579',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def call_orientator() -> discord.Embed:
    return discord.Embed(
        title='📢 Calling an Orientor',
        description=r"""A member will reach out to set up an Orientation.
Make sure that you have set up and tested your mods!

The Recruit Handbook can be found here:
https://docs.bourbonwarfare.com/wiki/welcome-to-bw/recruit-handbook

Please provide some idea of your availability below for an Orientation!""",
        colour=ENVIRONMENT.embed_colour_member(),
    )


def not_a_recruit() -> discord.Embed:
    return discord.Embed(
        title='❌ You are not a recruit',
        description='This command is intended for those only with a recruit role.',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def modlist_html() -> discord.Embed:
    return discord.Embed(
        title='📄 Latest Modlist',
        description='Use this to import the current modlist into the A3 Launcher.',
        url='https://mods.bourbonwarfare.com',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def modlist_website() -> discord.Embed:
    return discord.Embed(
        title='📄 CLICK HERE for Latest Modlist',
        description='This website will let you download the latest modlist.',
        url='https://mods.bourbonwarfare.com',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def docs_website() -> discord.Embed:
    return discord.Embed(
        title='📚 CLICK HERE for BW documentation',
        description='Link to BWs documentation and resources.',
        url='https://docs.bourbonwarfare.com',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def ping() -> discord.Embed:
    return discord.Embed(
        title='Pong! 🥔',
        description='Hello, world!',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def next_session_time(time: datetime.datetime) -> discord.Embed:
    timestamp = int(time.timestamp())
    return discord.Embed(
        title='🕓 Session Time Helper',
        description=f"""Next session will be:

**<t:{timestamp}:F>**

*Roughly* <t:{timestamp}:R>""",
        colour=ENVIRONMENT.embed_colour_member(),
    )


def relative_session_time(
    default_session_time: datetime.datetime, offset: float, relative_time: datetime.datetime
) -> discord.Embed:
    return discord.Embed(
        title='🕓 Session Time Helper',
        description=f"""The requested time relative to session time
<t:{int(default_session_time.timestamp())}:t> **{'+' if offset >= 0.0 else '-'}{abs(offset)}** is:

**<t:{int(relative_time.timestamp())}:t>**""",
        colour=ENVIRONMENT.embed_colour_member(),
    )


def login_with_discord(state: str) -> discord.Embed:
    redirect_uri = urllib.parse.quote(ENVIRONMENT.discord_oauth_redirect_uri(), safe='')
    return discord.Embed(
        title='Login to POTBOT with Discord',
        description='Logs into POTBOT to perform restricted commands.',
        url=f'https://discord.com/oauth2/authorize?client_id={ENVIRONMENT.discord_client_id()}&response_type=code&redirect_uri={redirect_uri}&scope=identify&state={state}',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def already_logged_in() -> discord.Embed:
    return discord.Embed(
        title="You are already logged in!",
        colour=ENVIRONMENT.embed_colour_member(),
    )


def logged_in_with_discord() -> discord.Embed:
    return discord.Embed(
        title="You've successfully logged in!",
        colour=ENVIRONMENT.embed_colour_member(),
    )


def failed_to_login_with_discord() -> discord.Embed:
    return discord.Embed(
        title='An error occured, you have not been logged in.',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def successful_arma_server_operation(user: discord.User, operation: str, server: str, server_status: str, hc_status: str, startup_status: str) -> discord.Embed:
    embed = discord.Embed(
        title='Success!',
        description=f'{user.mention} has succesfully performed "{operation}" on server {server}',
        colour=ENVIRONMENT.embed_colour_staff(),
    )
    embed.add_field(name='Server Status', value=server_status, inline=True)
    embed.add_field(name='HC Status', value=hc_status, inline=True)
    embed.add_field(name='Process Status', value=startup_status, inline=True)
    return embed


def arma_server_not_found(user: discord.User, operation: str, server: str) -> discord.Embed:
    return discord.Embed(
        title='What server are you talking about?',
        description=f'{user.mention} has tried to perform "{operation}" on server {server}, but "{server}" does not exist!',
        colour=ENVIRONMENT.embed_colour_staff(),
    )

def failed_arma_server_operation(user: discord.User, operation: str, server: str) -> discord.Embed:
    return discord.Embed(
        title='Failure :(', description=f'{user.mention} tried "{operation}" but it has failed on server {server}', colour=ENVIRONMENT.embed_colour_staff()
    )


def arma_server_status(server: str, mission: str, state: str, map: str, players: int, max_players: int) -> discord.Embed:
    embed = discord.Embed(
        title=f'Status of server "{server}"',
        colour=ENVIRONMENT.embed_colour_staff(),
    )
    embed.add_field(name='Mission', value=mission, inline=True)
    embed.add_field(name='Server State', value=state, inline=True)
    embed.add_field(name='Map', value=map, inline=True)
    embed.add_field(name='Players', value=f'{players}/{max_players}', inline=True)
    return embed