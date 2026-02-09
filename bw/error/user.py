from bw.error.base import BwDiscordError


class UserError(BwDiscordError):
    def __init__(self, reason: str):
        super().__init__(reason)


class ReauthNeeded(UserError):
    def __init__(self):
        super().__init__('Session needs to be refreshed')
