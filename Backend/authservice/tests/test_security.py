import json
from unittest.mock import patch, MagicMock

import pytest
from jose import JWTError

from config import security
from config.security import validate_cognito_token, _get_cognito_jwk_keys


FAKE_JWK_KEYS = [
    {"kid": "key-1", "kty": "RSA", "n": "fake-n", "e": "AQAB"},
    {"kid": "key-2", "kty": "RSA", "n": "fake-n-2", "e": "AQAB"},
]


@pytest.fixture(autouse=True)
def clear_jwk_cache():
    """Limpia la caché de JWK entre tests."""
    security._jwk_keys = None
    yield
    security._jwk_keys = None


def test_get_cognito_jwk_keys_fetches_and_caches():
    """Verifica que las claves JWK se descargan y cachean."""
    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({"keys": FAKE_JWK_KEYS}).encode()

    with patch("config.security.urlopen", return_value=fake_response) as mock_urlopen:
        keys = _get_cognito_jwk_keys()
        assert len(keys) == 2
        assert keys[0]["kid"] == "key-1"

        # Segunda llamada no debe hacer fetch (caché)
        keys2 = _get_cognito_jwk_keys()
        assert keys2 == keys
        mock_urlopen.assert_called_once()


def test_validate_cognito_token_success():
    """Token válido es decodificado correctamente."""
    expected_payload = {
        "sub": "cognito-uuid",
        "username": "admin@travelhub.com",
        "token_use": "access",
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_test",
    }

    security._jwk_keys = FAKE_JWK_KEYS

    with patch("config.security.jwt.get_unverified_header", return_value={"kid": "key-1"}):
        with patch("config.security.jwt.decode", return_value=expected_payload):
            payload = validate_cognito_token("valid-token")

    assert payload["sub"] == "cognito-uuid"
    assert payload["username"] == "admin@travelhub.com"
    assert payload["token_use"] == "access"


def test_validate_cognito_token_kid_not_found():
    """Token con kid no reconocido lanza JWTError."""
    security._jwk_keys = FAKE_JWK_KEYS

    with patch("config.security.jwt.get_unverified_header", return_value={"kid": "unknown-key"}):
        with pytest.raises(JWTError, match="Clave pública JWK no encontrada"):
            validate_cognito_token("bad-kid-token")


def test_validate_cognito_token_invalid_token_use():
    """Token con token_use inválido lanza JWTError."""
    security._jwk_keys = FAKE_JWK_KEYS

    with patch("config.security.jwt.get_unverified_header", return_value={"kid": "key-1"}):
        with patch("config.security.jwt.decode", return_value={"sub": "uuid", "token_use": "invalid"}):
            with pytest.raises(JWTError, match="Tipo de token no reconocido"):
                validate_cognito_token("bad-use-token")


def test_validate_cognito_token_expired():
    """Token expirado lanza JWTError (propagado desde jose)."""
    security._jwk_keys = FAKE_JWK_KEYS

    with patch("config.security.jwt.get_unverified_header", return_value={"kid": "key-1"}):
        with patch("config.security.jwt.decode", side_effect=JWTError("Token expired")):
            with pytest.raises(JWTError):
                validate_cognito_token("expired-token")
