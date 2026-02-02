from dataclasses import dataclass
from typing import NewType, Self
from bw.models.session import Session
import datetime

OAuthToken = NewType('OAuthToken', str)
OAuthRefreshToken = NewType('OAuthRefreshToken', str)
SessionToken = NewType('SessionToken', str)

@dataclass
class OAuthSession:
    access_token: OAuthToken
    refresh_token: OAuthRefreshToken
    expire_time: datetime.datetime

    def is_expired(self) -> bool:
        return (datetime.datetime.now() + datetime.timedelta(seconds=10)) > self.expire_time

    @classmethod
    def from_session(cls, session: Session) -> Self:
        return cls(
            access_token=session.oauth_token,
            refresh_token=session.oauth_refresh_token,
            expire_time = session.session_start + datetime.timedelta(seconds=session.expires_seconds)
        )

@dataclass
class BwSession:
    token: SessionToken
    expire_time: datetime.datetime

    @classmethod
    def null(cls) -> Self:
        return BwSession(
            token='potato',
            expire_time=datetime.datetime(year=2000, month=1, day=1)
        )
    
    @classmethod
    def from_session(cls, session: Session) -> Self:
        return cls(
            token=session.session_token,
            expire_time = session.session_expire
        )

    def is_expired(self) -> bool:
        return (datetime.datetime.now() + datetime.timedelta(seconds=10)) > self.expire_time
