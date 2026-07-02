from bw.error.arma import NoSessionInProgress
from sqlalchemy import select
from uuid import UUID

from bw.models.arma import ArmaSessionMessage
from bw.state import State


class ArmaApi:
    def create_session_message(self, state: State, session_id: UUID, message_id: int):
        with state.Session.begin() as session:
            new_session = ArmaSessionMessage(session_id=session_id, message_id=message_id)
            session.add(new_session)

    def inform_coop_played(self, state: State, session_id: UUID):
        with state.Session.begin() as session:
            query = select(ArmaSessionMessage).where(ArmaSessionMessage.session_id == session_id)
            arma_session = session.execute(query).scalar()
            if not arma_session:
                raise NoSessionInProgress(session_id)

            arma_session.has_coop_ended = True

    def has_coop_been_played(self, state: State, session_id: UUID):
        with state.Session.begin() as session:
            query = select(ArmaSessionMessage).where(ArmaSessionMessage.session_id == session_id)
            arma_session = session.execute(query).scalar()
            if not arma_session:
                raise NoSessionInProgress(session_id)

            return arma_session.has_coop_ended

    def session_notification_message(self, state: State, session_id: UUID):
        with state.Session.begin() as session:
            query = select(ArmaSessionMessage).where(ArmaSessionMessage.session_id == session_id)
            arma_session = session.execute(query).scalar()
            if not arma_session:
                raise NoSessionInProgress(session_id)

            return arma_session.message_id
