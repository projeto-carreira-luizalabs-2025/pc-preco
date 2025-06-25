from pytest import fixture
from app.api.common.auth_handler import do_auth


@fixture
def mock_do_auth(app):
    """
    Mocando o do_auth
    """
    app.dependency_overrides[do_auth] = lambda: None
    yield
    # Limpando o override
    app.dependency_overrides[do_auth] = {}
