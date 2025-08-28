from typing import Self


class Endpoint:
    endpoint: str

    @classmethod
    def get(cls) -> 'Resolver':
        return Resolver(cls())


class Resolver:
    endpoint: Endpoint
    path: list[str]

    def __init__(self, endpoint: Endpoint):
        self.endpoint = endpoint
        self.path = [endpoint.endpoint]

    def __getattr__(self, attr: str) -> Self:
        next = self.endpoint.__getattribute__(attr)
        self.path.append(next.endpoint)
        self.endpoint = next
        return self

    def resolve(self) -> str:
        return ''.join(self.path)
