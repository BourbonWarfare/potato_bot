from bw.endpoints.endpoint import Endpoint, VariableEndpoint, VariableResolver

class Discord(Endpoint):
    endpoint = 'discord'

class Bot(Endpoint):
    endpoint = 'bot'


class Login(Endpoint):
    endpoint = 'login'
    discord = Discord()
    bot = Bot()


class Auth(Endpoint):
    endpoint = 'auth'
    login = Login()
