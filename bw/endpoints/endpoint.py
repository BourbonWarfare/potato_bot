from typing import Self
from urllib.parse import quote_plus


class VariableEndpoint:
    pass


class Endpoint:
    endpoint: str | VariableEndpoint

    @classmethod
    def get(cls) -> 'Resolver':
        return Resolver(cls())


class VariableResolver:
    resolver: 'Resolver'

    def __init__(self, resolver: 'Resolver'):
        self.resolver = resolver

    def var(self, value: str) -> 'Resolver':
        self.resolver.path.append(f'{quote_plus(value)}/')
        return self.resolver


class Resolver:
    endpoint: Endpoint
    path: list[str]

    def __init__(self, endpoint: Endpoint):
        self.endpoint = endpoint
        self.path = [endpoint.endpoint]

    def __getattr__(self, attr: str) -> Self | VariableResolver:
        next = self.endpoint.__getattribute__(attr)
        self.endpoint = next
        if isinstance(next.endpoint, VariableEndpoint):
            return VariableResolver(self)
        self.path.append(next.endpoint)
        return self

    def resolve(self) -> str:
        return '/'.join(self.path)
