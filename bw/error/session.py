from bw.error.base import BwDiscordError


class SessionError(BwDiscordError):
    def __init__(self, reason: str):
        super().__init__(reason)


class RefreshFailed(SessionError):
    def __init__(self, error: Exception):
        super().__init__(f'Could not refresh OAuth token: {error}')


class NoSuchSession(SessionError):
    from bw.session.oauth import BwSession, OAuthSession

    session: None | BwSession | OAuthSession
    def __init__(self, session: None | BwSession | OAuthSession = None):
        super().__init__('No such session exists')
        self.session = session


class CannotLogin(SessionError):
    def __init__(self, context: str = ''):
        if context != '':
            super().__init__(f'An error has occured while logging in: {context}')
        else:
            super().__init__('An error has occured while logging in')

class SessionExpired(SessionError):
    def __init__(self):
        super().__init__('Session is expired')

class BwSessionExpired(SessionExpired):
    pass

class DiscordSessionExpired(SessionExpired):
    pass