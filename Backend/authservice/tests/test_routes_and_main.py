from fastapi.testclient import TestClient
from uuid import uuid4

from data.user import UserResponse
from main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to" in response.json()["message"]

def test_auth_health_endpoint():
    response = client.get("/auth/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_endpoint(monkeypatch, sample_user):
    cognito_result = {
        "AccessToken": "token-login",
        "IdToken": "id-token-login",
        "RefreshToken": "refresh-login",
        "ExpiresIn": 3600,
        "TokenType": "Bearer",
    }
    monkeypatch.setattr("api.routes.auth.AuthService.authenticate_user", lambda **_kwargs: cognito_result)

    response = client.post(
        "/auth/login",
        json={"email": "admin@travelhub.com", "password": "123456"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "token-login",
        "refresh_token": "refresh-login",
        "token_type": "bearer",
    }


def test_login_form_endpoint(monkeypatch):
    cognito_result = {
        "AccessToken": "token-form",
        "IdToken": "id-token-form",
        "RefreshToken": "refresh-form",
        "ExpiresIn": 3600,
        "TokenType": "Bearer",
    }
    monkeypatch.setattr("api.routes.auth.AuthService.authenticate_user", lambda **_kwargs: cognito_result)

    response = client.post(
        "/auth/login/form",
        data={"username": "admin@travelhub.com", "password": "123456"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "token-form"
    assert response.json()["refresh_token"] == "refresh-form"


def test_me_endpoint(monkeypatch, sample_user):
    def _fake_current_user():
        return UserResponse(
            id_usuario=sample_user.id_usuario,
            email=sample_user.email,
            full_name=sample_user.full_name,
            rol=sample_user.rol,
            partner_id=None,
        )

    app.dependency_overrides = {}
    from api.dependencies.auth import get_current_user

    app.dependency_overrides[get_current_user] = _fake_current_user

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == sample_user.email
    assert response.json()["full_name"] == sample_user.full_name
    app.dependency_overrides = {}


def test_refresh_endpoint(monkeypatch):
    cognito_result = {
        "AccessToken": "new-access-token",
        "IdToken": "new-id-token",
        "ExpiresIn": 3600,
        "TokenType": "Bearer",
    }
    monkeypatch.setattr("api.routes.auth.AuthService.refresh_tokens", lambda **_kwargs: cognito_result)

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "refresh-current", "email": "admin@travelhub.com"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "new-access-token"
    # Cognito no retorna un nuevo refresh token; se mantiene el original
    assert response.json()["refresh_token"] == "refresh-current"


def test_register_endpoint(monkeypatch):
    monkeypatch.setattr(
        "api.routes.auth.AuthService.register_user",
        lambda **_kwargs: {
            "CodeDeliveryDetails": {
                "Destination": "a***@mail.com",
                "DeliveryMedium": "EMAIL",
            }
        },
    )
    monkeypatch.setattr(
        "api.routes.auth.UserService.create_or_update_registered_user",
        lambda **_kwargs: object(),
    )

    response = client.post(
        "/auth/register",
        json={
            "first_name": "Ana",
            "last_name": "Gomez",
            "email": "ana@travelhub.com",
            "phone_number": "+573001234567",
            "password": "Str0ng!Pass",
        },
    )

    assert response.status_code == 201
    assert response.json()["delivery_medium"] == "EMAIL"


def test_register_endpoint_password_policy_validation():
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Ana",
            "last_name": "Gomez",
            "email": "ana@travelhub.com",
            "phone_number": "+573001234567",
            "password": "weak",
        },
    )

    assert response.status_code == 422


def test_register_endpoint_requires_international_phone_prefix():
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Ana",
            "last_name": "Gomez",
            "email": "ana2@travelhub.com",
            "phone_number": "3001234567",
            "password": "Str0ng!Pass",
        },
    )

    assert response.status_code == 422


def test_confirm_register_endpoint(monkeypatch):
    monkeypatch.setattr("api.routes.auth.AuthService.confirm_registration", lambda **_kwargs: None)
    monkeypatch.setattr("api.routes.auth.UserService.activate_user", lambda **_kwargs: True)

    response = client.post(
        "/auth/register/confirm",
        json={"email": "ana@travelhub.com", "code": "123456"},
    )

    assert response.status_code == 200
    assert "Cuenta confirmada" in response.json()["message"]
