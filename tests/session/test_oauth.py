import datetime
from types import SimpleNamespace

from bw.session.oauth import BwSession, OAuthSession


def future(seconds: int = 60):
    return datetime.datetime.now() + datetime.timedelta(seconds=seconds)


def past(seconds: int = 60):
    return datetime.datetime.now() - datetime.timedelta(seconds=seconds)


def test__oauth_session__header_contains_authorization():
    session = OAuthSession(access_token='access', refresh_token='refresh', expire_time=future())

    assert 'Authorization' in session.as_header()


def test__oauth_session__expires_with_safety_window():
    assert OAuthSession(access_token='a', refresh_token='r', expire_time=future(60)).is_expired() is False
    assert OAuthSession(access_token='a', refresh_token='r', expire_time=future(5)).is_expired() is True


def test__oauth_session__from_session_uses_session_start_plus_expires_seconds():
    start = datetime.datetime(2024, 1, 1, 12, 0, 0)
    row = SimpleNamespace(oauth_token='access', oauth_refresh_token='refresh', session_start=start, expires_seconds=30)

    session = OAuthSession.from_session(row)

    assert session.access_token == row.oauth_token
    assert session.refresh_token == row.oauth_refresh_token
    assert session.expire_time == start + datetime.timedelta(seconds=row.expires_seconds)


def test__bw_session__header_contains_authorization():
    session = BwSession(token='session', expire_time=future())

    assert 'Authorization' in session.as_header()


def test__bw_session__expires_with_safety_window():
    assert BwSession(token='session', expire_time=future(60)).is_expired() is False
    assert BwSession(token='session', expire_time=past()).is_expired() is True


def test__bw_session__from_session_uses_stored_backend_session():
    row = SimpleNamespace(session_token='session', session_expire=future())

    session = BwSession.from_session(row)

    assert session.token == row.session_token
    assert session.expire_time == row.session_expire
