from fastapi.testclient import TestClient

from data.user import UserResponse
from main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to" in response.json()["message"]


def test_login_endpoint(monkeypatch, sample_user):
    monkeypatch.setattr("api.routes.auth.AuthService.authenticate_user", lambda **_kwargs: sample_user)
    monkeypatch.setattr("api.routes.auth.create_access_token", lambda **_kwargs: "token-login")

    response = client.post(
        "/auth/login",
        json={"email": sample_user.email, "password": "123456"},
    )

    assert response.status_code == 200
    assert response.json() == {"access_token": "token-login", "token_type": "bearer"}


def test_login_form_endpoint(monkeypatch, sample_user):
    monkeypatch.setattr("api.routes.auth.AuthService.authenticate_user", lambda **_kwargs: sample_user)
    monkeypatch.setattr("api.routes.auth.create_access_token", lambda **_kwargs: "token-form")

    response = client.post(
        "/auth/login/form",
        data={"username": sample_user.email, "password": "123456"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "token-form"


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


def test_refresh_endpoint(monkeypatch, sample_user):
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
    monkeypatch.setattr("api.routes.auth.create_access_token", lambda **_kwargs: "token-refresh")

    response = client.post("/auth/refresh")

    assert response.status_code == 200
    assert response.json()["access_token"] == "token-refresh"
    app.dependency_overrides = {}
