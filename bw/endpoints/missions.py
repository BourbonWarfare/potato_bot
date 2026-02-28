from bw.endpoints.endpoint import Endpoint, VariableEndpoint


class Server(Endpoint):
    endpoint = VariableEndpoint()


class Upload(Endpoint):
    endpoint = 'upload'
    server = Server()


class Missions(Endpoint):
    endpoint = 'missions'
    upload = Upload()
