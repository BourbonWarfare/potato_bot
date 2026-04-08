from bw.endpoints.endpoint import Endpoint

class Sse(Endpoint):
    endpoint = 'sse'

class Realtime(Endpoint):
    endpoint = 'realtime'
    sse = Sse()
