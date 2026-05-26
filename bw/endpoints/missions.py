from bw.endpoints.endpoint import Endpoint, VariableEndpoint


class MissionId(Endpoint):
    endpoint = VariableEndpoint()


class Mission(Endpoint):
    endpoint = 'mission'
    mission_id = MissionId()


class IterationId(Endpoint):
    endpoint = VariableEndpoint()


class Iteration(Endpoint):
    endpoint = 'iteration'
    iteration_id = IterationId()


class Server(Endpoint):
    endpoint = VariableEndpoint()


class Upload(Endpoint):
    endpoint = 'upload'
    server = Server()


class Missions(Endpoint):
    endpoint = 'missions'
    upload = Upload()
    iteration = Iteration()
    mission = Mission()
