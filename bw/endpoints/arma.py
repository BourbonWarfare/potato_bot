from bw.endpoints.endpoint import Endpoint, VariableEndpoint


class Start(Endpoint):
    endpoint = 'start'


class Stop(Endpoint):
    endpoint = 'stop'


class Restart(Endpoint):
    endpoint = 'restart'


class Update(Endpoint):
    endpoint = 'update'


class UpdateMods(Endpoint):
    endpoint = 'update_mods'


class Healthcheck(Endpoint):
    endpoint = 'healthcheck'


class Server(Endpoint):
    endpoint = VariableEndpoint()
    start = Start()
    stop = Stop()
    restart = Restart()
    update = Update()
    update_mods = UpdateMods()
    healthcheck = Healthcheck()


class Arma(Endpoint):
    endpoint = 'arma/'
    server = Server()


class ServerOps(Endpoint):
    endpoint = 'server_ops/'
    arma = Arma()
