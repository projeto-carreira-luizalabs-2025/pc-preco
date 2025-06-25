import pytest
from app.api.common.auth_handler import do_auth
from unittest.mock import patch


class DummyKeycloakAdapter:
    async def validate_token(self, token):
        return {"sellers": "1,2,3"}


@pytest.mark.asyncio
async def test_do_auth_success(monkeypatch):
    # Arrange
    token = "valid_token"
    seller_id = "2"
    adapter = DummyKeycloakAdapter()

    # Act
    result = await do_auth(token=token, seller_id=seller_id, openid_adapter=adapter)

    # Assert
    assert result is None  # do_auth returns nothing if successful


@pytest.mark.asyncio
async def test_do_auth_unauthorized(monkeypatch):
    # Arrange
    token = "invalid_token"
    seller_id = "1"

    class DummyAdapter:
        async def validate_token(self, token):
            raise Exception("OAuthException")

    # Patch OAuthException to be raised
    with patch("app.api.common.auth_handler.OAuthException", Exception):
        with pytest.raises(Exception):  # UnauthorizedException is a subclass of Exception
            await do_auth(token=token, seller_id=seller_id, openid_adapter=DummyAdapter())


@pytest.mark.asyncio
async def test_do_auth_forbidden(monkeypatch):
    # Arrange
    token = "valid_token"
    seller_id = "99"  # Not in sellers

    class DummyAdapter:
        async def validate_token(self, token):
            return {"sellers": "1,2,3"}

    with pytest.raises(Exception) as excinfo:
        await do_auth(token=token, seller_id=seller_id, openid_adapter=DummyAdapter())
    assert "Forbidden" in str(excinfo.value)


@pytest.mark.asyncio
async def test_do_auth_no_sellers(monkeypatch):
    # Arrange
    token = "valid_token"
    seller_id = "1"

    class DummyAdapter:
        async def validate_token(self, token):
            return {}

    with pytest.raises(Exception) as excinfo:
        await do_auth(token=token, seller_id=seller_id, openid_adapter=DummyAdapter())
    assert "Forbidden" in str(excinfo.value)
