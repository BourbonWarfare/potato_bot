from typing import Self
from urllib.parse import quote_plus


class VariableEndpoint:
    pass


class Endpoint:
    endpoint: str | VariableEndpoint

    @classmethod
    def get(cls) -> 'Resolver':
        return Resolver(cls())


class Resolver:
    endpoint: Endpoint
    path: list[str]

    def __init__(self, endpoint: Endpoint):
        self.endpoint = endpoint
        # Roots are always concrete string endpoints; variable endpoints only
        # appear mid-chain and are populated via .var().
        assert isinstance(endpoint.endpoint, str), 'Resolver root must be a string endpoint'
        self.path = [endpoint.endpoint]

    def __getattr__(self, attr: str) -> Self:
        next = self.endpoint.__getattribute__(attr)
        self.endpoint = next
        if not isinstance(next.endpoint, VariableEndpoint):
            self.path.append(next.endpoint)
        return self

    def var(self, value: str) -> Self:
        assert isinstance(self.endpoint.endpoint, VariableEndpoint), (
            f'.var() called on non-variable endpoint {type(self.endpoint).__name__}'
        )
        self.path.append(quote_plus(value))
        return self

    def resolve(self) -> str:
        return '/'.join(self.path)
