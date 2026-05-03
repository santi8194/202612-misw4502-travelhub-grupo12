from unittest.mock import MagicMock, patch
from types import SimpleNamespace

import pytest
from botocore.exceptions import ClientError
from fastapi import HTTPException

from modules.auth_service import AuthService, _compute_secret_hash, _validate_cognito_settings, _get_cognito_client


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


def test_register_user_success():
    mock_client = MagicMock()
    mock_client.sign_up.return_value = {
        "UserSub": "abc-123",
        "CodeDeliveryDetails": {
            "Destination": "a***@mail.com",
            "DeliveryMedium": "EMAIL",
        },
    }

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        result = AuthService.register_user(
            email="new@travelhub.com",
            password="Str0ng!Pass",
            first_name="Ana",
            last_name="Gomez",
            phone_number="+573001234567",
        )

    assert result["UserSub"] == "abc-123"
    mock_client.sign_up.assert_called_once()


def test_register_user_username_exists():
    mock_client = MagicMock()
    mock_client.sign_up.side_effect = _make_client_error("UsernameExistsException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.register_user(
                email="existing@travelhub.com",
                password="Str0ng!Pass",
                first_name="Ana",
                last_name="Gomez",
                phone_number="+573001234567",
            )

    assert exc.value.status_code == 409


def test_confirm_registration_success():
    mock_client = MagicMock()
    mock_client.confirm_sign_up.return_value = {}

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        AuthService.confirm_registration(email="new@travelhub.com", code="123456")

    mock_client.confirm_sign_up.assert_called_once()


def test_confirm_registration_invalid_code():
    mock_client = MagicMock()
    mock_client.confirm_sign_up.side_effect = _make_client_error("CodeMismatchException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.confirm_registration(email="new@travelhub.com", code="111111")

    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# _validate_cognito_settings tests
# ---------------------------------------------------------------------------

def test_validate_cognito_settings_missing_region(monkeypatch):
    monkeypatch.setattr(
        "modules.auth_service.settings",
        SimpleNamespace(COGNITO_REGION="", COGNITO_CLIENT_ID="id", COGNITO_CLIENT_SECRET="secret"),
    )
    with pytest.raises(HTTPException) as exc:
        _validate_cognito_settings()
    assert exc.value.status_code == 503
    assert "COGNITO_REGION" in exc.value.detail


def test_validate_cognito_settings_missing_client_id(monkeypatch):
    monkeypatch.setattr(
        "modules.auth_service.settings",
        SimpleNamespace(COGNITO_REGION="us-east-1", COGNITO_CLIENT_ID="", COGNITO_CLIENT_SECRET="secret"),
    )
    with pytest.raises(HTTPException) as exc:
        _validate_cognito_settings()
    assert exc.value.status_code == 503
    assert "COGNITO_CLIENT_ID" in exc.value.detail


def test_validate_cognito_settings_missing_secret(monkeypatch):
    monkeypatch.setattr(
        "modules.auth_service.settings",
        SimpleNamespace(COGNITO_REGION="us-east-1", COGNITO_CLIENT_ID="id", COGNITO_CLIENT_SECRET=""),
    )
    with pytest.raises(HTTPException) as exc:
        _validate_cognito_settings()
    assert exc.value.status_code == 503
    assert "COGNITO_CLIENT_SECRET" in exc.value.detail


# ---------------------------------------------------------------------------
# _get_cognito_client tests
# ---------------------------------------------------------------------------

def test_get_cognito_client_value_error(monkeypatch):
    monkeypatch.setattr(
        "modules.auth_service.settings",
        SimpleNamespace(COGNITO_REGION="invalid", COGNITO_CLIENT_ID="id", COGNITO_CLIENT_SECRET="secret"),
    )
    with patch("modules.auth_service.boto3.client", side_effect=ValueError("bad region")):
        with pytest.raises(HTTPException) as exc:
            _get_cognito_client()
    assert exc.value.status_code == 503


# ---------------------------------------------------------------------------
# register_user additional error cases
# ---------------------------------------------------------------------------

def test_register_user_invalid_password():
    mock_client = MagicMock()
    mock_client.sign_up.side_effect = _make_client_error("InvalidPasswordException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.register_user(
                email="new@travelhub.com",
                password="weak",
                first_name="Ana",
                last_name="Gomez",
                phone_number="+573001234567",
            )
    assert exc.value.status_code == 400


def test_register_user_invalid_parameter():
    mock_client = MagicMock()
    mock_client.sign_up.side_effect = _make_client_error("InvalidParameterException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.register_user(
                email="new@travelhub.com",
                password="Str0ng!Pass",
                first_name="Ana",
                last_name="Gomez",
                phone_number="invalid",
            )
    assert exc.value.status_code == 400


def test_register_user_too_many_requests():
    mock_client = MagicMock()
    mock_client.sign_up.side_effect = _make_client_error("TooManyRequestsException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.register_user(
                email="new@travelhub.com",
                password="Str0ng!Pass",
                first_name="Ana",
                last_name="Gomez",
                phone_number="+573001234567",
            )
    assert exc.value.status_code == 429


def test_register_user_unknown_error():
    mock_client = MagicMock()
    mock_client.sign_up.side_effect = _make_client_error("InternalErrorException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.register_user(
                email="new@travelhub.com",
                password="Str0ng!Pass",
                first_name="Ana",
                last_name="Gomez",
                phone_number="+573001234567",
            )
    assert exc.value.status_code == 500


# ---------------------------------------------------------------------------
# confirm_registration additional error cases
# ---------------------------------------------------------------------------

def test_confirm_registration_expired_code():
    mock_client = MagicMock()
    mock_client.confirm_sign_up.side_effect = _make_client_error("ExpiredCodeException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.confirm_registration(email="new@travelhub.com", code="123456")
    assert exc.value.status_code == 400


def test_confirm_registration_user_not_found():
    mock_client = MagicMock()
    mock_client.confirm_sign_up.side_effect = _make_client_error("UserNotFoundException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.confirm_registration(email="missing@travelhub.com", code="123456")
    assert exc.value.status_code == 404


def test_confirm_registration_already_confirmed():
    mock_client = MagicMock()
    mock_client.confirm_sign_up.side_effect = _make_client_error("NotAuthorizedException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.confirm_registration(email="confirmed@travelhub.com", code="123456")
    assert exc.value.status_code == 409


def test_confirm_registration_too_many_requests():
    mock_client = MagicMock()
    mock_client.confirm_sign_up.side_effect = _make_client_error("TooManyRequestsException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.confirm_registration(email="new@travelhub.com", code="123456")
    assert exc.value.status_code == 429


def test_confirm_registration_unknown_error():
    mock_client = MagicMock()
    mock_client.confirm_sign_up.side_effect = _make_client_error("InternalErrorException")

    with patch("modules.auth_service._get_cognito_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc:
            AuthService.confirm_registration(email="new@travelhub.com", code="123456")
    assert exc.value.status_code == 500
