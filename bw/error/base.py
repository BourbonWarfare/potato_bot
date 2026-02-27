class BwDiscordError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class StateUsedBeforeDefined(BwDiscordError):
    def __init__(self):
        super().__init__('Attempting to use State instance before it has been setup')