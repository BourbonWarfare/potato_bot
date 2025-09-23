from bw.error.base import BwDiscordError

class InterfaceError(BwDiscordError):
    def __init__(self, message: str):
        super().__init__(f'An error occured talking to the backend: {message}')

class StartError(InterfaceError):
    def __init__(self, status: int, message: str):
        super().__init__(f'Cant start server: {status} {message}')

class StopError(InterfaceError):
    def __init__(self, status: int, message: str):
        super().__init__(f'Cant stop server: {status} {message}')

class RestartError(InterfaceError):
    def __init__(self, status: int, message: str):
        super().__init__(f'Cant restart server: {status} {message}')

class UpdateError(InterfaceError):
    def __init__(self, status: int, message: str):
        super().__init__(f'Cant update server: {status} {message}')

class UpdateModsError(InterfaceError):
    def __init__(self, status: int, message: str):
        super().__init__(f'Cant update server modpack: {status} {message}')

class HealthcheckError(InterfaceError):
    def __init__(self, status: int, message: str):
        super().__init__(f'Cant perform healthcheck on server: {status} {message}')