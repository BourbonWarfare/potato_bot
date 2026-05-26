"""aiohttp.ClientSession patching helpers — enough to exercise our request shape
and our response parsing without standing up a real server."""

from typing import Any

import aiohttp
import pytest


class FakeResponse:
    """Async-context-manager stand-in for aiohttp.ClientResponse."""

    def __init__(self, payload: Any = None, status: int = 200):
        self._payload = payload
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise aiohttp.ClientResponseError(
                request_info=None,
                history=(),
                status=self.status,
                message=f'HTTP {self.status}',
            )

    async def json(self) -> Any:
        return self._payload

    async def text(self) -> str:
        return str(self._payload)


class RecordingSession:
    """Stand-in for aiohttp.ClientSession that records calls and yields a configurable FakeResponse."""

    def __init__(self, response: FakeResponse, *, init_headers: dict | None = None):
        self.response = response
        self.init_headers = init_headers or {}
        self.calls: list[dict[str, Any]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def _record(self, method: str, url: str, **kwargs):
        self.calls.append({'method': method, 'url': url, **kwargs})
        return self.response

    def get(self, url: str, **kwargs):
        return self._record('GET', url, **kwargs)

    def post(self, url: str, **kwargs):
        return self._record('POST', url, **kwargs)


@pytest.fixture
def fake_aiohttp_session(mocker):
    """Returns a factory: call with a FakeResponse to install a RecordingSession on aiohttp.ClientSession.

    The returned RecordingSession captures every request the code under test made, including the
    headers passed to ClientSession(headers=...)."""

    def install(response: FakeResponse) -> RecordingSession:
        session = RecordingSession(response)

        def constructor(*args, headers=None, **kwargs):
            session.init_headers = headers or {}
            return session

        mocker.patch('aiohttp.ClientSession', side_effect=constructor)
        return session

    return install
