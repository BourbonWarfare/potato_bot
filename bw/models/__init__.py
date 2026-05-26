from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase

from bw.discord.types import ForumId
from bw.session.types import (
    DiscordSnowflake,
    OAuthRefreshToken,
    OAuthToken,
    SessionToken,
)


class Base(DeclarativeBase):
    type_annotation_map = {
        DiscordSnowflake: String,
        OAuthToken: String,
        OAuthRefreshToken: String,
        SessionToken: String,
        ForumId: BigInteger,
    }
