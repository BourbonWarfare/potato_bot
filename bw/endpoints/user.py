from bw.endpoints.endpoint import Endpoint


class RoleCreate(Endpoint):
    endpoint = 'create'


class Assign(Endpoint):
    endpoint = 'assign'


class Role(Endpoint):
    endpoint = 'role'
    create = RoleCreate()
    assign = Assign()


class Bot(Endpoint):
    endpoint = 'bot'


class UserCreate(Endpoint):
    endpoint = 'create'
    bot = Bot()


class User(Endpoint):
    endpoint = 'user'
    role = Role()
    create = UserCreate()
