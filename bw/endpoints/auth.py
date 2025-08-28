from bw.endpoints.endpoint import Endpoint


class Bot(Endpoint):
    endpoint = 'bot'


class Login(Endpoint):
    endpoint = 'login/'
    bot = Bot()


class Auth(Endpoint):
    endpoint = 'auth/'
    login = Login()
