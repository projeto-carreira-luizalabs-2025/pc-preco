from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import jwt
import pytest

from app.integrations.auth.keycloak_adapter import (
    InvalidTokenException,
    KeycloakAdapter,
    OAuthException,
    TokenExpiredException,
)

WELL_KNOWN_URL = "https://keycloak.example.com/.well-known/openid-configuration"
WELL_KNOWN_DATA = {
    "authorization_endpoint": "https://keycloak.example.com/auth",
    "jwks_uri": "https://keycloak.example.com/jwks",
}
JWKS_DATA = {"keys": [{"kid": "abc123", "alg": "RS256", "kty": "RSA", "use": "sig", "n": "foo", "e": "AQAB"}]}
TOKEN = "header.payload.signature"
HEADER = {"kid": "abc123", "alg": "RS256"}


@pytest.fixture
def adapter():
    return KeycloakAdapter(WELL_KNOWN_URL)


def test_get_well_knwon_fetches_and_caches(adapter):
    with patch.object(httpx, "Client") as mock_client:
        mock_instance = mock_client.return_value.__enter__.return_value
        mock_instance.get.return_value.json.return_value = WELL_KNOWN_DATA
        mock_instance.get.return_value.raise_for_status = lambda: None

        result = adapter.get_well_knwon()
        assert result == WELL_KNOWN_DATA

        result2 = adapter.get_well_knwon()
        assert result2 == WELL_KNOWN_DATA
        assert mock_instance.get.call_count == 1


def test_get_authorization_endpoint(adapter):
    with patch.object(KeycloakAdapter, "get_well_knwon", return_value=WELL_KNOWN_DATA):
        assert adapter.get_authorization_endpoint() == WELL_KNOWN_DATA["authorization_endpoint"]


@pytest.mark.asyncio
async def test_get_public_keys_fetches_and_caches(adapter):
    with patch.object(KeycloakAdapter, "get_well_knwon", return_value=WELL_KNOWN_DATA):
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = JWKS_DATA
            mock_response.raise_for_status = lambda: None
            mock_get.return_value = mock_response

            keys = await adapter.get_public_keys()
            assert keys == JWKS_DATA["keys"]

            keys2 = await adapter.get_public_keys()
            assert keys2 == JWKS_DATA["keys"]
            assert mock_get.call_count == 1


def test_get_token_header():
    with patch("jwt.get_unverified_header", return_value=HEADER) as mock_header:
        header = KeycloakAdapter.get_token_header(TOKEN)
        assert header == HEADER
        mock_header.assert_called_once_with(TOKEN)


def test_get_header_info_from_token():
    with patch("jwt.get_unverified_header", return_value=HEADER):
        kid, alg = KeycloakAdapter.get_header_info_from_token(TOKEN)
        assert kid == "abc123"
        assert alg == "RS256"


@pytest.mark.asyncio
async def test_get_alg_key_for_kid_success(adapter):
    adapter._public_keys = JWKS_DATA["keys"]
    key = await adapter.get_alg_key_for_kid("abc123")
    assert key["kid"] == "abc123"


@pytest.mark.asyncio
async def test_get_alg_key_for_kid_not_found(adapter):
    adapter._public_keys = JWKS_DATA["keys"]
    with pytest.raises(InvalidTokenException):
        await adapter.get_alg_key_for_kid("notfound")


@pytest.mark.asyncio
async def test_validate_token_success(adapter):
    with patch.object(KeycloakAdapter, "get_header_info_from_token", return_value=("abc123", "RS256")):
        with patch.object(KeycloakAdapter, "get_alg_key_for_kid", return_value=JWKS_DATA["keys"][0]):
            with patch("jwt.PyJWK", return_value="jwk") as mock_jwk:
                with patch("jwt.decode", return_value={"sub": "user"}) as mock_decode:
                    result = await adapter.validate_token(TOKEN)
                    assert result == {"sub": "user"}
                    mock_jwk.assert_called_once_with(jwk_data=JWKS_DATA["keys"][0], algorithm="RS256")
                    mock_decode.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "jwt_exc,expected_exc",
    [
        (jwt.ExpiredSignatureError, TokenExpiredException),
        (jwt.InvalidTokenError, InvalidTokenException),
    ],
)
async def test_validate_token_jwt_errors(adapter, jwt_exc, expected_exc):
    with patch.object(KeycloakAdapter, "get_header_info_from_token", return_value=("abc123", "RS256")):
        with patch.object(KeycloakAdapter, "get_alg_key_for_kid", return_value=JWKS_DATA["keys"][0]):
            with patch("jwt.PyJWK", return_value="jwk"):
                with patch("jwt.decode", side_effect=jwt_exc):
                    with pytest.raises(expected_exc):
                        await adapter.validate_token(TOKEN)


@pytest.mark.asyncio
async def test_validate_token_other_exception(adapter):
    with patch.object(KeycloakAdapter, "get_header_info_from_token", return_value=("abc123", "RS256")):
        with patch.object(KeycloakAdapter, "get_alg_key_for_kid", return_value=JWKS_DATA["keys"][0]):
            with patch("jwt.PyJWK", return_value="jwk"):
                with patch("jwt.decode", side_effect=Exception("fail")):
                    with pytest.raises(OAuthException):
                        await adapter.validate_token(TOKEN)
