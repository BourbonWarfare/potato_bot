import discord
from discord.ext import commands


def require_guild(interaction: discord.Interaction) -> discord.Guild:
    if interaction.guild is None:
        raise RuntimeError('This command must be used in a guild')
    return interaction.guild


def require_member(interaction: discord.Interaction) -> discord.Member:
    if not isinstance(interaction.user, discord.Member):
        raise RuntimeError('This command must be used by a guild member')
    return interaction.user


def require_role(guild: discord.Guild, role_id: int, name: str) -> discord.Role:
    role = guild.get_role(role_id)
    if role is None:
        raise RuntimeError(f'Missing configured role {name} ({role_id})')
    return role


def require_text_channel(bot: commands.Bot | discord.Client, channel_id: int, name: str) -> discord.TextChannel:
    channel = bot.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        raise RuntimeError(f'Missing configured text channel {name} ({channel_id})')
    return channel


def require_messageable_channel(
    bot: commands.Bot | discord.Client, channel_id: int, name: str
) -> discord.TextChannel | discord.Thread:
    channel = bot.get_channel(channel_id)
    if not isinstance(channel, (discord.TextChannel, discord.Thread)):
        raise RuntimeError(f'Missing configured messageable channel {name} ({channel_id})')
    return channel


def require_rdp_channel(
    bot: commands.Bot | discord.Client, channel_id: int, name: str
) -> discord.TextChannel | discord.VoiceChannel:
    channel = bot.get_channel(channel_id)
    if not isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
        raise RuntimeError(f'Missing configured RDP channel {name} ({channel_id})')
    return channel
