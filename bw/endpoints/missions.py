from bw.endpoints.endpoint import Endpoint


class Upload(Endpoint):
    endpoint = 'upload'


class Missions(Endpoint):
    endpoint = 'missions'
    upload = Upload()
