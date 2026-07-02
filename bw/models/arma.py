from sqlalchemy import Uuid, BigInteger, Boolean
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from bw.models import Base


class ArmaSessionMessage(Base):
    __tablename__ = 'arma_session_messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[UUID] = mapped_column(Uuid)
    message_id: Mapped[int] = mapped_column(BigInteger)
    has_coop_ended: Mapped[bool] = mapped_column(Boolean)
