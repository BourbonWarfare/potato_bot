import uuid

from sqlalchemy import BigInteger, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from bw.models import Base
from bw.discord.types import ForumId


class MissionForum(Base):
    __tablename__ = 'mission_forums'

    id: Mapped[int] = mapped_column(primary_key=True)

    thread_id: Mapped[ForumId] = mapped_column(BigInteger, unique=True, nullable=False)
    mission_uuid: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True, nullable=False)
