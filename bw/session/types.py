class DiscordSnowflake(str):
    def __new__(cls, value: str | int) -> 'DiscordSnowflake':
        return super().__new__(cls, str(value))

    def __repr__(self) -> str:
        return f'DiscordSnowflake({super().__repr__()})'


class OAuthToken(str):
    def __new__(cls, value: str) -> 'OAuthToken':
        return super().__new__(cls, str(value))

    def __repr__(self) -> str:
        return f'OAuthToken({super().__repr__()})'


class OAuthRefreshToken(str):
    def __new__(cls, value: str) -> 'OAuthRefreshToken':
        return super().__new__(cls, str(value))

    def __repr__(self) -> str:
        return f'OAuthRefreshToken({super().__repr__()})'


class SessionToken(str):
    def __new__(cls, value: str) -> 'SessionToken':
        return super().__new__(cls, str(value))

    def __repr__(self) -> str:
        return f'SessionToken({super().__repr__()})'
