import aiohttp


class ResponseError(Exception):
    body: str
    exception: aiohttp.ClientResponseError

    def __init__(self, body: str, exception: aiohttp.ClientResponseError):
        self.body = body
        self.exception = exception
