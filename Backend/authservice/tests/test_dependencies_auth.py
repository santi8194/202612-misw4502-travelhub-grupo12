from datetime import timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from api.dependencies.auth import get_current_user
from config.config import settings
from config.security import create_access_token


def test_get_current_user_success(monkeypatch, sample_user):
    token = create_access_token(
        subject=str(sample_user.id_usuario),
        email=sample_user.email,
        rol=sample_user.rol,
        session_id="session-123",
        expires_delta=timedelta(minutes=5),
    )
    monkeypatch.setattr("api.dependencies.auth.UserService.get_user_by_email", lambda _email: sample_user)
    monkeypatch.setattr("api.dependencies.auth.SessionService.validate_session", lambda *_args, **_kwargs: True)

    current = get_current_user(token=token)

    assert current.email == sample_user.email
    assert current.rol == sample_user.rol


def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException) as exc:
        get_current_user(token="invalid-token")

    assert exc.value.status_code == 401


def test_get_current_user_token_without_sub():
    payload = {"email": "admin@travelhub.com", "rol": "ADMIN_HOTEL"}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token)

    assert exc.value.status_code == 401


def test_get_current_user_user_not_found(monkeypatch):
    token = create_access_token(
        subject="123",
        email="missing@travelhub.com",
        rol="USER",
        session_id="session-123",
        expires_delta=timedelta(minutes=5),
    )
    monkeypatch.setattr("api.dependencies.auth.UserService.get_user_by_email", lambda _email: None)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token)

    assert exc.value.status_code == 404


def test_get_current_user_rejects_inactive_session(monkeypatch, sample_user):
    token = create_access_token(
        subject=str(sample_user.id_usuario),
        email=sample_user.email,
        rol=sample_user.rol,
        session_id="session-123",
        expires_delta=timedelta(minutes=5),
    )
    monkeypatch.setattr("api.dependencies.auth.UserService.get_user_by_email", lambda _email: sample_user)
    monkeypatch.setattr("api.dependencies.auth.SessionService.validate_session", lambda *_args, **_kwargs: False)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token)

    assert exc.value.status_code == 401
