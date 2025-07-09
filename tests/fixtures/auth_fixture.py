import pytest
from fastapi import Request

from app.api.common.auth_handler import UserAuthInfo, do_auth, get_current_user
from app.models.base import UserModel


@pytest.fixture(autouse=True)
def mock_do_auth(app):
    async def fake_do_auth(request: Request):
        # Garante que trace_id existe para simular o middleware
        if not hasattr(request.state, "trace_id"):
            request.state.trace_id = "test-trace-id"
        user_info = UserAuthInfo(
            user=UserModel(name="test-user", server="test-issuer"),
            trace_id=request.state.trace_id,
            sellers=["1", "2", "3"],
        )
        request.state.user = user_info
        return user_info

    async def fake_get_current_user(request: Request):
        return getattr(request.state, "user", None)

    app.dependency_overrides[do_auth] = fake_do_auth
    app.dependency_overrides[get_current_user] = fake_get_current_user
    yield
    app.dependency_overrides.pop(do_auth, None)
    app.dependency_overrides.pop(get_current_user, None)
