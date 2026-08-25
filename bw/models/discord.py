import uuid

from sqlalchemy import BigInteger, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from bw.discord.types import ForumId
from bw.models import Base


class MissionForum(Base):
    __tablename__ = 'mission_forums'

    id: Mapped[int] = mapped_column(primary_key=True)

    thread_id: Mapped[ForumId] = mapped_column(BigInteger, unique=True, nullable=False)
    mission_uuid: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True, nullable=False)
