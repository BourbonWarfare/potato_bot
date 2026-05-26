import uuid

import pytest

from bw.events.decoder import ServerSentEvent


def make_event(namespace: str, event: str, data: dict | None = None, id: uuid.UUID | None = None) -> ServerSentEvent:
    return ServerSentEvent(
        id=id if id is not None else uuid.UUID(int=0),
        event=event,
        namespace=namespace,
        data=data if data is not None else {},
    )


@pytest.fixture
def uploaded_event():
    return make_event(
        'mission',
        'uploaded',
        {'mission': '11111111-2222-3333-4444-555555555555', 'iteration': '11111111-2222-3333-4444-555555555555'},
    )


@pytest.fixture
def reviewed_event():
    return make_event(
        'mission',
        'reviewed',
        {'iteration': '11111111-2222-3333-4444-555555555555', 'review': '99999999-2222-3333-4444-555555555555'},
    )


@pytest.fixture
def cosigned_event():
    return make_event('mission', 'cosigned', {'review': '99999999-2222-3333-4444-555555555555'})


@pytest.fixture
def unknown_event():
    return make_event('mission', 'flagged', {})
