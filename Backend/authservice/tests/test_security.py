from datetime import timedelta
from uuid import uuid4

from jose import jwt

from config.config import settings
from config.security import create_access_token, create_refresh_token, get_password_hash, hash_token, verify_password


def test_password_hash_and_verify_success():
    hashed = get_password_hash("123456")
    assert verify_password("123456", hashed) is True


def test_password_hash_and_verify_failure():
    hashed = get_password_hash("123456")
    assert verify_password("654321", hashed) is False


def test_create_access_token_with_partner_id():
    token = create_access_token(
        subject=str(uuid4()),
        email="admin@travelhub.com",
        rol="ADMIN_HOTEL",
        partner_id="partner-123",
        session_id="session-123",
        expires_delta=timedelta(minutes=5),
    )

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["email"] == "admin@travelhub.com"
    assert payload["rol"] == "ADMIN_HOTEL"
    assert payload["partner_id"] == "partner-123"
    assert payload["sid"] == "session-123"
    assert "exp" in payload


def test_create_access_token_without_partner_id():
    token = create_access_token(
        subject="user-id",
        email="user@travelhub.com",
        rol="USER",
        expires_delta=timedelta(minutes=5),
    )

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user-id"
    assert "partner_id" not in payload


def test_refresh_token_generation_and_hashing():
    refresh_token = create_refresh_token()

    assert isinstance(refresh_token, str)
    assert len(refresh_token) > 20
    assert hash_token(refresh_token) != refresh_token
