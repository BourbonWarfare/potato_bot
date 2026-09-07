import pytest

from bw.endpoints import Root
from bw.endpoints.endpoint import Endpoint, VariableEndpoint


def test__endpoint_resolver__returns_a_path_for_concrete_endpoint():
    path = Root.get().api.v1.healthcheck.resolve()

    assert path


def test__endpoint_resolver__encodes_variable_values():
    path = Root.get().api.v1.server_ops.arma.server.var('main server').status.resolve()

    assert ' ' not in path
    assert path != Root.get().api.v1.server_ops.arma.server.var('mainserver').status.resolve()


def test__endpoint_resolver__var_on_concrete_endpoint_raises():
    with pytest.raises(AssertionError):
        Root.get().api.v1.healthcheck.var('unexpected')


def test__endpoint_resolver__variable_root_is_rejected():
    class BadRoot(Endpoint):
        endpoint = VariableEndpoint()

    with pytest.raises(AssertionError):
        BadRoot.get()
