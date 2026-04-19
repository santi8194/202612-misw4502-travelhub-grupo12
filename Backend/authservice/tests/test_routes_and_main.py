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
    monkeypatch.setattr("api.routes.auth.AuthService.authenticate_user", lambda **_kwargs: sample_user)
    monkeypatch.setattr(
        "api.routes.auth.SessionService.create_session",
        lambda _user_id: SimpleNamespace(id=uuid4(), refresh_token="refresh-login"),
    )
    monkeypatch.setattr("api.routes.auth.create_access_token", lambda **_kwargs: "token-login")

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
            rol=sample_user.rol,
            partner_id=None,
        )

    app.dependency_overrides = {}
    from api.dependencies.auth import get_current_user

    app.dependency_overrides[get_current_user] = _fake_current_user

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == sample_user.email
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
