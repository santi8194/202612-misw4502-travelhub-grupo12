from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from config.config import settings
from modules.auth_service import AuthService, _failed_logins


def test_authenticate_user_success(monkeypatch, sample_user):
    monkeypatch.setattr("modules.auth_service.UserService.get_user_by_email", lambda _email: sample_user)
    monkeypatch.setattr("modules.auth_service.verify_password", lambda _plain, _hash: True)

    _failed_logins[sample_user.email] = (2, None)
    user = AuthService.authenticate_user(sample_user.email, "123456")

    assert user.email == sample_user.email
    assert sample_user.email not in _failed_logins


def test_authenticate_user_user_not_found(monkeypatch):
    monkeypatch.setattr("modules.auth_service.UserService.get_user_by_email", lambda _email: None)

    with pytest.raises(HTTPException) as exc:
        AuthService.authenticate_user("missing@travelhub.com", "123456")

    assert exc.value.status_code == 401
    assert _failed_logins["missing@travelhub.com"][0] == 1


def test_authenticate_user_wrong_password(monkeypatch, sample_user):
    monkeypatch.setattr("modules.auth_service.UserService.get_user_by_email", lambda _email: sample_user)
    monkeypatch.setattr("modules.auth_service.verify_password", lambda _plain, _hash: False)

    with pytest.raises(HTTPException) as exc:
        AuthService.authenticate_user(sample_user.email, "wrong")

    assert exc.value.status_code == 401
    assert _failed_logins[sample_user.email][0] == 1


def test_authenticate_user_locked_out(monkeypatch):
    email = "blocked@travelhub.com"
    _failed_logins[email] = (5, datetime.utcnow() + timedelta(minutes=10))

    with pytest.raises(HTTPException) as exc:
        AuthService.authenticate_user(email, "123456")

    assert exc.value.status_code == 429


def test_record_failed_attempt_sets_lockout(monkeypatch):
    monkeypatch.setattr(settings, "MAX_LOGIN_ATTEMPTS", 2)
    monkeypatch.setattr(settings, "LOCKOUT_DURATION_MINUTES", 1)

    email = "lock@travelhub.com"
    AuthService._record_failed_attempt(email)
    assert _failed_logins[email][0] == 1
    assert _failed_logins[email][1] is None

    AuthService._record_failed_attempt(email)
    attempts, lockout_until = _failed_logins[email]
    assert attempts == 2
    assert lockout_until is not None


def test_is_locked_out_false_after_expiry():
    email = "expired@travelhub.com"
    _failed_logins[email] = (5, datetime.utcnow() - timedelta(seconds=1))

    assert AuthService._is_locked_out(email) is False
