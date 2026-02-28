from bw.endpoints.endpoint import Endpoint
from bw.endpoints.auth import Auth
from bw.endpoints.user import User
from bw.endpoints.group import Group
from bw.endpoints.arma import ServerOps
from bw.endpoints.missions import Missions


class Healthcheck(Endpoint):
    endpoint = 'healthcheck'


class V1(Endpoint):
    endpoint = 'v1'
    server_ops = ServerOps()
    auth = Auth()
    user = User()
    group = Group()
    missions = Missions()
    healthcheck = Healthcheck()


class Local(Endpoint):
    endpoint = 'local'
    user = User()


class Api(Endpoint):
    endpoint = 'api'
    v1 = V1()
    local = Local()


class Root(Endpoint):
    endpoint = ''
    api = Api()
