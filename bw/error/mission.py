from bw.error.base import BwDiscordError

class NoServersToUploadTo(BwDiscordError):
    def __init__(self):
        super().__init__('Cannot upload to BW Backend due to no servers being found')
