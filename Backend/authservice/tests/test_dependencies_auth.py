import pytest
from fastapi import HTTPException
from jose import JWTError

from api.dependencies.auth import get_current_user


def test_get_current_user_success_access_token(monkeypatch, sample_user):
    """Valida que un access token de Cognito (campo 'username') funcione correctamente."""
    monkeypatch.setattr(
        "api.dependencies.auth.validate_cognito_token",
        lambda _token: {"sub": "cognito-uuid", "username": sample_user.email, "token_use": "access"},
    )
    monkeypatch.setattr("api.dependencies.auth.UserService.get_user_by_email", lambda _email: sample_user)

    current = get_current_user(token="valid-cognito-token")

    assert current.email == sample_user.email
    assert current.rol == sample_user.rol


def test_get_current_user_success_id_token(monkeypatch, sample_user):
    """Valida que un ID token de Cognito (campo 'email') funcione correctamente."""
    monkeypatch.setattr(
        "api.dependencies.auth.validate_cognito_token",
        lambda _token: {"sub": "cognito-uuid", "email": sample_user.email, "token_use": "id"},
    )
    monkeypatch.setattr("api.dependencies.auth.UserService.get_user_by_email", lambda _email: sample_user)

    current = get_current_user(token="valid-id-token")

    assert current.email == sample_user.email


def test_get_current_user_invalid_token(monkeypatch):
    """Token inválido provoca 401."""
    monkeypatch.setattr(
        "api.dependencies.auth.validate_cognito_token",
        lambda _token: (_ for _ in ()).throw(JWTError("invalid")),
    )

    with pytest.raises(HTTPException) as exc:
        get_current_user(token="invalid-token")

    assert exc.value.status_code == 401


def test_get_current_user_token_without_email(monkeypatch):
    """Token sin email ni username provoca 401."""
    monkeypatch.setattr(
        "api.dependencies.auth.validate_cognito_token",
        lambda _token: {"sub": "cognito-uuid", "token_use": "access"},
    )

    with pytest.raises(HTTPException) as exc:
        get_current_user(token="no-email-token")

    assert exc.value.status_code == 401


def test_get_current_user_user_not_found(monkeypatch):
    """Usuario no encontrado en la BD provoca 404."""
    monkeypatch.setattr(
        "api.dependencies.auth.validate_cognito_token",
        lambda _token: {"sub": "cognito-uuid", "username": "missing@travelhub.com", "token_use": "access"},
    )
    monkeypatch.setattr("api.dependencies.auth.UserService.get_user_by_email", lambda _email: None)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token="valid-token")

    assert exc.value.status_code == 404
