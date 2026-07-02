from uuid import UUID
from bw.error.base import BwDiscordError


class ArmaError(BwDiscordError):
    def __init__(self, reason: str):
        super().__init__(reason)


class NoSessionInProgress(ArmaError):
    def __init__(self, session_id: UUID):
        super().__init__(f'No session with ID {session_id} is in progress')
