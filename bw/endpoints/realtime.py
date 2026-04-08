from bw.endpoints.endpoint import Endpoint

class Subscribe(Endpoint):
    endpoint = 'subscribe'

class Realtime(Endpoint):
    endpoint = 'realtime'
    subscribe = Subscribe()
