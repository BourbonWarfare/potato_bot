from types import SimpleNamespace

import pytest

from bw.commands.community import require_existing_session
from bw.error import NoSuchSession


class FakeSession:
    def __init__(self, expired: bool):
        self.expired = expired

    def is_expired(self) -> bool:
        return self.expired


class FakeSessionApi:
    def __init__(self, *, oauth_expired=False, bw_expired=False):
        self.oauth_session = FakeSession(oauth_expired)
        self.bw_session = FakeSession(bw_expired)

    def get_discord_session_from_discord_id(self, *_):
        return self.oauth_session

    def get_bw_session_from_discord_id(self, *_):
        return self.bw_session


@pytest.mark.parametrize(
    ('oauth_expired', 'bw_expired'),
    [
        (True, False),
        (False, True),
    ],
)
def test__require_existing_session__raises_when_stored_auth_cannot_be_used(mocker, oauth_expired, bw_expired):
    mocker.patch(
        'bw.commands.community.SessionApi',
        return_value=FakeSessionApi(oauth_expired=oauth_expired, bw_expired=bw_expired),
    )
    mocker.patch('bw.commands.community.State')

    with pytest.raises(NoSuchSession):
        require_existing_session(SimpleNamespace(id=1))


def test__require_existing_session__returns_sessions_when_stored_auth_is_usable(mocker):
    api = FakeSessionApi()
    mocker.patch('bw.commands.community.SessionApi', return_value=api)
    mocker.patch('bw.commands.community.State')

    bw_session, oauth_session = require_existing_session(SimpleNamespace(id=1))

    assert bw_session is api.bw_session
    assert oauth_session is api.oauth_session
