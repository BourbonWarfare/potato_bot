from dataclasses import dataclass
from typing import Self
from bw.models.session import Session
from bw.session.types import OAuthToken, OAuthRefreshToken, SessionToken
import datetime


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
            expire_time=session.session_start + datetime.timedelta(seconds=session.expires_seconds),
        )

    def as_header(self) -> dict:
        return {'Authorization': f'Bearer {self.access_token}'}


@dataclass
class BwSession:
    token: SessionToken
    expire_time: datetime.datetime

    @classmethod
    def from_session(cls, session: Session) -> Self:
        return cls(token=session.session_token, expire_time=session.session_expire)

    def is_expired(self) -> bool:
        return (datetime.datetime.now() + datetime.timedelta(seconds=10)) > self.expire_time

    def as_header(self) -> dict:
        return {'Authorization': f'Bearer {self.token}'}
