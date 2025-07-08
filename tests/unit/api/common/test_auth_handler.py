import pytest
from app.api.common.auth_handler import do_auth
from unittest.mock import patch, MagicMock


class DummyKeycloakAdapter:
    async def validate_token(self, token):
        return {"sellers": "1,2,3", "sub": "user", "iss": "issuer"}


def make_request(trace_id="trace123"):
    mock_request = MagicMock()
    mock_request.state = MagicMock()
    mock_request.state.trace_id = trace_id
    return mock_request


@pytest.mark.asyncio
async def test_do_auth_success(monkeypatch):
    # Arrange
    token = "valid_token"
    seller_id = "2"
    adapter = DummyKeycloakAdapter()
    request = make_request()
    # Act
    result = await do_auth(request=request, token=token, seller_id=seller_id, openid_adapter=adapter)

    # Assert
    assert result is not None
    assert result.user.name == "user"
    assert result.sellers == ["1", "2", "3"]


@pytest.mark.asyncio
async def test_do_auth_unauthorized(monkeypatch):
    # Arrange
    token = "invalid_token"
    seller_id = "1"
    request = make_request()

    class DummyAdapter:
        async def validate_token(self, token):
            raise Exception("OAuthException")

    # Patch OAuthException to be raised
    with patch("app.api.common.auth_handler.OAuthException", Exception):
        with pytest.raises(Exception):  # UnauthorizedException is a subclass of Exception
            await do_auth(request=request, token=token, seller_id=seller_id, openid_adapter=DummyAdapter())


@pytest.mark.asyncio
async def test_do_auth_forbidden(monkeypatch):
    token = "valid_token"
    seller_id = "99"
    request = make_request()

    class DummyAdapter:
        async def validate_token(self, token):
            return {"sellers": "1,2,3", "sub": "user", "iss": "issuer"}

    with pytest.raises(Exception) as excinfo:
        await do_auth(request=request, token=token, seller_id=seller_id, openid_adapter=DummyAdapter())
    assert "Forbidden" in str(excinfo.value) or "não autorizado" in str(excinfo.value)


@pytest.mark.asyncio
async def test_do_auth_no_sellers(monkeypatch):
    token = "valid_token"
    seller_id = "1"
    request = make_request()

    class DummyAdapter:
        async def validate_token(self, token):
            return {"sub": "user", "iss": "issuer"}

    with pytest.raises(Exception) as excinfo:
        await do_auth(request=request, token=token, seller_id=seller_id, openid_adapter=DummyAdapter())
    assert "Forbidden" in str(excinfo.value) or "não autorizado" in str(excinfo.value)
