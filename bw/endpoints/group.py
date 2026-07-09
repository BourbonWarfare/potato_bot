from bw.endpoints.endpoint import Endpoint


class Permission(Endpoint):
    endpoint = 'permission'


class List(Endpoint):
    endpoint = 'list'


class Create(Endpoint):
    endpoint = 'create'
    permission = Permission()


class Join(Endpoint):
    endpoint = 'join'


class Leave(Endpoint):
    endpoint = 'leave'


class Group(Endpoint):
    endpoint = 'group'
    create = Create()
    join = Join()
    leave = Leave()
