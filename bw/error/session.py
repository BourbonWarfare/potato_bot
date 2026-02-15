from bw.error.base import BwDiscordError


class SessionError(BwDiscordError):
    def __init__(self, reason: str):
        super().__init__(reason)


class RefreshFailed(SessionError):
    def __init__(self):
        super().__init__('Could not refresh OAuth token')


class NoSuchSession(SessionError):
    def __init__(self):
        super().__init__('No such session exists')


class CannotLogin(SessionError):
    def __init__(self, context: str = ''):
        if context != '':
            super().__init__(f'An error has occured while logging in: {context}')
        else:
            super().__init__('An error has occured while logging in')

class SessionExpired(SessionError):
    def __init__(self):
        super().__init__('Session is expired')

class BwSessionExpired(SessionError):
    pass

class DiscordSessionExpired(SessionError):
    pass