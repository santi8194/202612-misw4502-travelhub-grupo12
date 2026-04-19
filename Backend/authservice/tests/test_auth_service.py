from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from fastapi import HTTPException

from modules.auth_service import AuthService, _compute_secret_hash


def _make_client_error(code: str, message: str = "error") -> ClientError:
    return ClientError(
        {"Error": {"Code": code, "Message": message}},
        "initiate_auth",
    )


def test_authenticate_user_success(cognito_auth_result):
    mock_client = MagicMock()
    mock_client.initiate_auth.return_value = {"AuthenticationResult": cognito_auth_result}

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        result = AuthService.authenticate_user("admin@travelhub.com", "123456")

    assert result["AccessToken"] == "fake-access-token"
    assert result["RefreshToken"] == "fake-refresh-token"
    mock_client.initiate_auth.assert_called_once()


def test_authenticate_user_wrong_password():
    mock_client = MagicMock()
    mock_client.initiate_auth.side_effect = _make_client_error("NotAuthorizedException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.authenticate_user("admin@travelhub.com", "wrong")

    assert exc.value.status_code == 401


def test_authenticate_user_not_found():
    mock_client = MagicMock()
    mock_client.initiate_auth.side_effect = _make_client_error("UserNotFoundException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.authenticate_user("missing@travelhub.com", "123456")

    assert exc.value.status_code == 401


def test_authenticate_user_not_confirmed():
    mock_client = MagicMock()
    mock_client.initiate_auth.side_effect = _make_client_error("UserNotConfirmedException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.authenticate_user("unconfirmed@travelhub.com", "123456")

    assert exc.value.status_code == 403


def test_authenticate_user_too_many_requests():
    mock_client = MagicMock()
    mock_client.initiate_auth.side_effect = _make_client_error("TooManyRequestsException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.authenticate_user("admin@travelhub.com", "123456")

    assert exc.value.status_code == 429


def test_authenticate_user_unknown_error():
    mock_client = MagicMock()
    mock_client.initiate_auth.side_effect = _make_client_error("InternalErrorException", "unexpected")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.authenticate_user("admin@travelhub.com", "123456")

    assert exc.value.status_code == 500


def test_refresh_tokens_success(cognito_refresh_result):
    mock_client = MagicMock()
    mock_client.initiate_auth.return_value = {"AuthenticationResult": cognito_refresh_result}

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        result = AuthService.refresh_tokens("refresh-token", "admin@travelhub.com")

    assert result["AccessToken"] == "new-access-token"
    mock_client.initiate_auth.assert_called_once()


def test_refresh_tokens_expired():
    mock_client = MagicMock()
    mock_client.initiate_auth.side_effect = _make_client_error("NotAuthorizedException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.refresh_tokens("expired-token", "admin@travelhub.com")

    assert exc.value.status_code == 401


def test_refresh_tokens_internal_error():
    mock_client = MagicMock()
    mock_client.initiate_auth.side_effect = _make_client_error("InternalErrorException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.refresh_tokens("token", "admin@travelhub.com")

    assert exc.value.status_code == 500


def test_compute_secret_hash():
    result = _compute_secret_hash("test@example.com")
    assert isinstance(result, str)
    assert len(result) > 0
