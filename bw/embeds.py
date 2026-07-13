import discord
import datetime
import urllib.parse
from typing import Any
from bw.environment import ENVIRONMENT
from bw.missions.response import IterationInformationResponse, MissionInformationResponse, MissionTypeResponse


def default() -> discord.Embed:
    return discord.Embed(
        title="Someone hasn't configured something",
        description="This is the default embed that occurs when we don't know what to put yet",
        colour=ENVIRONMENT.embed_colour_member(),
    )


def backend_failure() -> discord.Embed:
    return discord.Embed(
        title='🔨 Something is wrong with the server...',
        description='An error has occured that the bot cannot handle. Please ping techmods.',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def not_permitted() -> discord.Embed:
    return discord.Embed(
        title='❌ You are not allowed to do that',
        description='You have tried to perform an action that you do not have permissions for',
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
        url=f'https://discord.com/oauth2/authorize?client_id={ENVIRONMENT.discord_client_id()}'
        f'&response_type=code&redirect_uri={redirect_uri}&scope=identify&state={state}',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def already_logged_in() -> discord.Embed:
    return discord.Embed(
        title='You are already logged in!',
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


def successful_arma_server_operation(
    user: discord.User, operation: str, server: str, server_status: str, hc_status: str, startup_status: str
) -> discord.Embed:
    embed = discord.Embed(
        title='Success!',
        description=f'{user.mention} has succesfully performed "{operation}" on server {server}',
        colour=ENVIRONMENT.embed_colour_staff(),
    )
    embed.add_field(name='Server Status', value=server_status, inline=True)
    embed.add_field(name='HC Status', value=hc_status, inline=True)
    embed.add_field(name='Process Status', value=startup_status, inline=True)
    return embed


def arma_server_not_found(user: discord.User, server: str) -> discord.Embed:
    return discord.Embed(
        title='What server are you talking about?',
        description=f'{user.mention} has tried to operate on server {server}, but "{server}" does not exist!',
        colour=ENVIRONMENT.embed_colour_staff(),
    )


def arma_server_unresponsive(user: discord.User, server: str) -> discord.Embed:
    return discord.Embed(
        title='ARMA server Unresponsive',
        description=f'{user.mention} has tried to operate on server {server}, but "{server}" is not responsive!',
        colour=ENVIRONMENT.embed_colour_staff(),
    )


def failed_arma_server_operation(user: discord.User, operation: str, server: str) -> discord.Embed:
    return discord.Embed(
        title='Failure :(',
        description=f'{user.mention} tried "{operation}" but it has failed on server {server}',
        colour=ENVIRONMENT.embed_colour_staff(),
    )


def couldnt_get_arma_server_status(
    user: discord.User, server: str, server_status: str, hc_status: str, startup_status: str
) -> discord.Embed:
    embed = discord.Embed(
        title='Failed!',
        description=f'{user.mention} has tried to get "{server}"\'s status, but it did not complete successfully',
        colour=ENVIRONMENT.embed_colour_staff(),
    )
    embed.add_field(name='Server Status', value=server_status, inline=True)
    embed.add_field(name='HC Status', value=hc_status, inline=True)
    embed.add_field(name='Process Status', value=startup_status, inline=True)
    return embed


def arma_server_status(server: str, mission: str, state: str, map: str, players: int, max_players: int) -> discord.Embed:
    embed = discord.Embed(
        title=f'Status of server "{server}"',
        colour=ENVIRONMENT.embed_colour_staff(),
    )
    embed.add_field(name='Mission', value=mission, inline=False)
    embed.add_field(name='Server State', value=state, inline=False)
    embed.add_field(name='Map', value=map, inline=False)
    embed.add_field(name='Players', value=f'{players}/{max_players}', inline=False)
    return embed


def arma_server_state(server: str, server_status: str, hc_status: str, startup_status: str) -> discord.Embed:
    embed = discord.Embed(
        title=f'Status of server "{server}"',
        colour=ENVIRONMENT.embed_colour_staff(),
    )
    embed.add_field(name='Server Status', value=server_status, inline=True)
    embed.add_field(name='HC Status', value=hc_status, inline=True)
    embed.add_field(name='Process Status', value=startup_status, inline=True)
    return embed


def successful_server_update(server: str, server_status: str, hc_status: str, startup_status: str) -> discord.Embed:
    embed = discord.Embed(
        title=f'Successfully updated "{server}"',
        colour=ENVIRONMENT.embed_colour_staff(),
    )
    embed.add_field(name='Server Status', value=server_status, inline=True)
    embed.add_field(name='HC Status', value=hc_status, inline=True)
    embed.add_field(name='Process Status', value=startup_status, inline=True)
    return embed


def server_management_failure(context: str) -> discord.Embed:
    return discord.Embed(
        title='🔨 Failed to operate on ARMA server',
        description=f'We could not complete the operation on the server: {context}',
        colour=ENVIRONMENT.embed_colour_staff(),
    )


def failed_to_reach_bw_backend() -> discord.Embed:
    return discord.Embed(
        title='🔨 Failed to reach BW Backend',
        description='Something is broken, we cannot reach the backend. Please try again later, or tell Staff if this persists.',
        colour=ENVIRONMENT.embed_colour_staff(),
    )


def failed_to_reach_discord() -> discord.Embed:
    return discord.Embed(
        title='🔨 Failed to reach Discord',
        description='Something is _really_ broken, we cannot reach Discord. Please try again later.',
        colour=ENVIRONMENT.embed_colour_staff(),
    )


def cannot_upload_no_servers() -> discord.Embed:
    return discord.Embed(
        title='🔨 Failed to upload: No servers',
        description='The BW backend reports no servers; it is probably shutdown, tell Staff to restart it.',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def mission_type_information(mission_type: MissionTypeResponse) -> discord.Embed:
    return discord.Embed(
        title='📋 Mission Type',
        description=f'Type: {mission_type.name}\nSignoffs needed: {mission_type.signoffs_required}',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def mission_information(mission: MissionInformationResponse) -> tuple[discord.Embed, discord.Embed]:
    return (
        discord.Embed(
            title='🪖 Mission Information',
            description=(
                f'🪧 Name: {mission.title}\n🖥️ Server: {mission.server}\n👀 Author: {mission.author_name}\n🗺️ Map: {mission.map}'
            ),
            colour=ENVIRONMENT.embed_colour_member(),
        ),
        mission_type_information(mission.mission_type),
    )


def iteration_information(iteration: IterationInformationResponse) -> discord.Embed:
    mission_length = f'{iteration.mission_length // 60:02d}:{iteration.mission_length % 60:02d}'
    safe_start_length = f'{iteration.safe_start_length // 60:02d}:{iteration.safe_start_length % 60:02d}'
    upload_timestamp = int(iteration.upload_date.timestamp())

    embed = discord.Embed(
        title=f'🆕 Iteration #{iteration.iteration}',
        description='\n'.join([f'{field}: {value}' for field, value in iteration.changelog.items()]),
        colour=ENVIRONMENT.embed_colour_member(),
    )
    embed.add_field(
        name='Players (min / desired / max)',
        value=f'{iteration.min_player_count} / {iteration.desired_player_count} / {iteration.max_player_count}',
        inline=False,
    )
    embed.add_field(name='Safe Start', value=safe_start_length, inline=True)
    embed.add_field(name='Mission Length', value=mission_length, inline=True)
    embed.add_field(name='BWMF Version', value=iteration.bwmf_version, inline=True)
    embed.add_field(name='Uploaded', value=f'<t:{upload_timestamp}:R>', inline=False)
    return embed


def upcoming_session() -> discord.Embed:
    embed = discord.Embed(
        title='⏰ Session is coming up!',
        description='@Members and @Recruits session time starts in one hour.\n'
        'Make sure that you have updated your mods.\n\n'
        'Use the bell to be pinged for Co-Op slotting.',
        colour=ENVIRONMENT.embed_colour_member(),
    )
    embed.set_image(
        url='https://cdn.discordapp.com/attachments/285837079139844096/724897893315641404/unknown.png?ex=6a1b4305&is=6a19f185&hm=f42610bea54e238a34e60309a141e865dc758f8e1e0bdbbd30677f67df1e5ff7&'
    )
    return embed


def safe_start_ended(mission: MissionInformationResponse, orbat: dict[str, Any]) -> discord.Embed:
    embed = discord.Embed(
        title=f'🦺 Safe Start has ended for {mission.title} by {mission.author_name} [{mission.mission_type.name} ]',
        description=f'{len(orbat)} players are present!',
        colour=ENVIRONMENT.embed_colour_member(),
    )
    embed.set_image(
        url='https://cdn.discordapp.com/attachments/285837079139844096/724897893315641404/unknown.png?ex=6a1b4305&is=6a19f185&hm=f42610bea54e238a34e60309a141e865dc758f8e1e0bdbbd30677f67df1e5ff7&'
    )
    return embed


def safe_start_ended_basic(orbat: dict[str, Any]) -> discord.Embed:
    embed = discord.Embed(
        title='🦺 Safe Start has ended!',
        description=f'{len(orbat)} players are present!',
        colour=ENVIRONMENT.embed_colour_member(),
    )
    embed.set_image(
        url='https://cdn.discordapp.com/attachments/285837079139844096/724897893315641404/unknown.png?ex=6a1b4305&is=6a19f185&hm=f42610bea54e238a34e60309a141e865dc758f8e1e0bdbbd30677f67df1e5ff7&'
    )
    return embed


def mission_ended(mission: MissionInformationResponse, orbat: dict[str, Any]) -> discord.Embed:
    all_groups: list[dict] = orbat['groups']

    id_to_name_map = {}
    for group in all_groups:
        for member in group['members']:
            id_to_name_map[member['steam_id']] = member['name']

    blufor_groups = [group for group in all_groups if group['side'] == 'WEST']
    opfor_groups = [group for group in all_groups if group['side'] == 'EAST']
    indfor_groups = [group for group in all_groups if group['side'] == 'GUER']
    civilian_groups = [group for group in all_groups if group['side'] == 'CIV']
    spectator_groups = [group for group in all_groups if group['side'] == 'LOGIC']

    blufor_string = '\n'.join(
        [f'{group["name"]}: {id_to_name_map[group["leader"]]} ({len(group["members"]) - 1} reports)' for group in blufor_groups]
    )
    opfor_string = '\n'.join(
        [f'{group["name"]}: {id_to_name_map[group["leader"]]} ({len(group["members"]) - 1} reports)' for group in opfor_groups]
    )
    indfor_string = '\n'.join(
        [f'{group["name"]}: {id_to_name_map[group["leader"]]} ({len(group["members"]) - 1} reports)' for group in indfor_groups]
    )
    civilian_string = '\n'.join(
        [f'{group["name"]}: {id_to_name_map[group["leader"]]} ({len(group["members"]) - 1} reports)' for group in civilian_groups]
    )
    spectator_string = f'{sum([len(group["members"]) for group in spectator_groups])} spectators'

    embed = discord.Embed(
        title=f'🏁 The {mission.mission_type.name} has finished!',
        description='\n'.join([blufor_string, opfor_string, indfor_string, civilian_string, spectator_string]),
        colour=ENVIRONMENT.embed_colour_member(),
    )
    return embed


def mission_ended_basic(orbat: dict[str, Any]) -> discord.Embed:
    all_groups: list[dict] = orbat['groups']

    id_to_name_map = {}
    for group in all_groups:
        for member in group['members']:
            id_to_name_map[member['steam_id']] = member['name']

    blufor_groups = [group for group in all_groups if group['side'] == 'WEST']
    opfor_groups = [group for group in all_groups if group['side'] == 'EAST']
    indfor_groups = [group for group in all_groups if group['side'] == 'GUER']
    civilian_groups = [group for group in all_groups if group['side'] == 'CIV']
    spectator_groups = [group for group in all_groups if group['side'] == 'LOGIC']

    blufor_string = '\n'.join(
        [f'{group["name"]}: {id_to_name_map[group["leader"]]} ({len(group["members"]) - 1} reports)' for group in blufor_groups]
    )
    opfor_string = '\n'.join(
        [f'{group["name"]}: {id_to_name_map[group["leader"]]} ({len(group["members"]) - 1} reports)' for group in opfor_groups]
    )
    indfor_string = '\n'.join(
        [f'{group["name"]}: {id_to_name_map[group["leader"]]} ({len(group["members"]) - 1} reports)' for group in indfor_groups]
    )
    civilian_string = '\n'.join(
        [f'{group["name"]}: {id_to_name_map[group["leader"]]} ({len(group["members"]) - 1} reports)' for group in civilian_groups]
    )
    spectator_string = f'{sum([len(group["members"]) for group in spectator_groups])} spectators'

    embed = discord.Embed(
        title='🏁 The mission has finished!',
        description='\n'.join([blufor_string, opfor_string, indfor_string, civilian_string, spectator_string]),
        colour=ENVIRONMENT.embed_colour_member(),
    )
    return embed


def failed_to_get_rpt(server: str, reason: str) -> discord.Embed:
    return discord.Embed(
        title='❌ Failed to get server RPT!',
        description=f'Could not get RPT for {server}: {reason}',
        colour=ENVIRONMENT.embed_colour_staff(),
    )


def successfully_joined_group(group: str) -> discord.Embed:
    return discord.Embed(
        title='📢 Joined group!',
        description=f'You are now apart of "{group}"',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def no_group_with_name(group: str) -> discord.Embed:
    return discord.Embed(
        title='📢 Could not join group!',
        description=f'No group called "{group}" exists',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def already_apart_of_group(group: str) -> discord.Embed:
    return discord.Embed(
        title='📢 Could not join group!',
        description=f'You are already apart of "{group}"',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def could_not_join_group(group: str) -> discord.Embed:
    return discord.Embed(
        title='📢 Could not join group!',
        description=f'Did not successfully join "{group}"',
        colour=ENVIRONMENT.embed_colour_member(),
    )


def cron_run(cron: str) -> discord.Embed:
    return discord.Embed(
        title=f'🤖 Cron {cron} is running!',
        colour=ENVIRONMENT.embed_colour_staff(),
    )


def server_event(event: str, server: str) -> discord.Embed:
    return discord.Embed(
        title=f'🖧 {server} has performed {event}!',
        colour=ENVIRONMENT.embed_colour_staff(),
    )
