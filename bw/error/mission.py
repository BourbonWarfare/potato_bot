from bw.error.base import BwDiscordError


class NoServersToUploadTo(BwDiscordError):
    def __init__(self):
        super().__init__('Cannot upload to BW Backend due to no servers being found')


class MisconfiguredForumChannel(BwDiscordError):
    def __init__(self, channel_info: str):
        super().__init__(f'Attempted to get a forum channel, but the following error occured: {channel_info}')
