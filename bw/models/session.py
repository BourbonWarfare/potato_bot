from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
import datetime

from bw.models import Base
from bw.session.types import DiscordSnowflake, SessionToken, OAuthToken, OAuthRefreshToken


class Session(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True)

    discord_id: Mapped[DiscordSnowflake] = mapped_column(unique=True, nullable=False)
    session_start: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=datetime.datetime.now
    )

    session_token: Mapped[SessionToken] = mapped_column(nullable=False)
    session_expire: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=datetime.datetime.now
    )

    oauth_token: Mapped[OAuthToken] = mapped_column(nullable=False)
    oauth_refresh_token: Mapped[OAuthRefreshToken] = mapped_column(nullable=False)
    expires_seconds: Mapped[int] = mapped_column(nullable=False)
