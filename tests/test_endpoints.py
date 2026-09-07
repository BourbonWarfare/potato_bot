import pytest

from bw.endpoints import Root
from bw.endpoints.endpoint import Endpoint, VariableEndpoint


def test__endpoint_resolver__resolves_concrete_path():
    assert Root.get().api.v1.healthcheck.resolve() == '/api/v1/healthcheck'


def test__endpoint_resolver__resolves_variable_path_with_url_encoding():
    path = Root.get().api.v1.server_ops.arma.server.var('main server').status.resolve()

    assert path == '/api/v1/server_ops/arma/main+server/status'


def test__endpoint_resolver__var_on_concrete_endpoint_raises_clear_error():
    with pytest.raises(AssertionError, match='non-variable endpoint'):
        Root.get().api.v1.healthcheck.var('unexpected')


def test__endpoint_resolver__variable_root_is_rejected():
    class BadRoot(Endpoint):
        endpoint = VariableEndpoint()

    with pytest.raises(AssertionError, match='Resolver root'):
        BadRoot.get()
