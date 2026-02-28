import aiohttp


class ResponseError(Exception):
    body: str
    exception: aiohttp.ClientResponseError

    def __init__(self, body: str, exception: aiohttp.ClientResponseError):
        self.body = body
        self.exception = exception

class CannotReachDiscord(Exception):
    def __init__(self):
        super().__init__('Failed to connect to Discord')

class CannotReachBwBackend(Exception):
    def __init__(self):
        super().__init__('Failed to connect to BW Backend')

