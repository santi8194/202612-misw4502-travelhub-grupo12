from fastapi.testclient import TestClient
from uuid import uuid4
from types import SimpleNamespace

from schemas.user import UserResponse
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


def test_get_user_by_id_endpoint(monkeypatch, sample_user):
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
    monkeypatch.setattr("api.routes.auth.UserService.get_user_by_id", lambda _user_id: sample_user)

    response = client.get(f"/auth/users/{sample_user.id_usuario}")

    assert response.status_code == 200
    assert response.json()["id_usuario"] == str(sample_user.id_usuario)
    assert response.json()["email"] == sample_user.email
    app.dependency_overrides = {}


def test_get_user_by_id_endpoint_returns_404(monkeypatch, sample_user):
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
    monkeypatch.setattr("api.routes.auth.UserService.get_user_by_id", lambda _user_id: None)

    response = client.get(f"/auth/users/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado"
    app.dependency_overrides = {}


def test_get_user_by_id_forbidden_when_requesting_another_user(monkeypatch, sample_user):
    another_user = SimpleNamespace(
        id_usuario=uuid4(),
        email="other@travelhub.com",
        full_name="Other User",
        rol="USER",
        partner_id=None,
    )

    def _fake_current_user():
        return UserResponse(
            id_usuario=sample_user.id_usuario,
            email=sample_user.email,
            full_name=sample_user.full_name,
            rol="USER",
            partner_id=None,
        )

    app.dependency_overrides = {}
    from api.dependencies.auth import get_current_user

    app.dependency_overrides[get_current_user] = _fake_current_user
    monkeypatch.setattr("api.routes.auth.UserService.get_user_by_id", lambda _user_id: another_user)

    response = client.get(f"/auth/users/{another_user.id_usuario}")

    assert response.status_code == 403
    assert response.json()["detail"] == "No tienes permisos para consultar este usuario"
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


def test_register_login_and_get_user_info_flow(monkeypatch):
    persisted_users = {}

    def _fake_register_user(**_kwargs):
        return {
            "UserSub": "cognito-sub-flow",
            "CodeDeliveryDetails": {
                "Destination": "f***@mail.com",
                "DeliveryMedium": "EMAIL",
            },
        }

    def _fake_create_or_update_registered_user(**kwargs):
        user_id = uuid4()
        user = SimpleNamespace(
            id_usuario=user_id,
            email=kwargs["email"],
            full_name=kwargs["full_name"],
            rol="USER",
            partner_id=None,
        )
        persisted_users[user_id] = user
        return user

    def _fake_authenticate_user(**kwargs):
        # Simulate a successful login only for previously persisted users.
        if not any(u.email == kwargs["email"] for u in persisted_users.values()):
            raise AssertionError("Login attempted for a non-persisted user")
        return {
            "AccessToken": "token-flow",
            "IdToken": "id-token-flow",
            "RefreshToken": "refresh-flow",
            "ExpiresIn": 3600,
            "TokenType": "Bearer",
        }

    def _fake_get_user_by_id(user_id):
        return persisted_users.get(user_id)

    monkeypatch.setattr("api.routes.auth.AuthService.register_user", _fake_register_user)
    monkeypatch.setattr(
        "api.routes.auth.UserService.create_or_update_registered_user",
        _fake_create_or_update_registered_user,
    )
    monkeypatch.setattr("api.routes.auth.AuthService.authenticate_user", _fake_authenticate_user)
    monkeypatch.setattr("api.routes.auth.UserService.get_user_by_id", _fake_get_user_by_id)

    register_response = client.post(
        "/auth/register",
        json={
            "first_name": "Flow",
            "last_name": "User",
            "email": "flow@travelhub.com",
            "phone_number": "+573001234567",
            "password": "Str0ng!Pass",
        },
    )

    assert register_response.status_code == 201
    assert len(persisted_users) == 1

    login_response = client.post(
        "/auth/login",
        json={"email": "flow@travelhub.com", "password": "Str0ng!Pass"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["access_token"] == "token-flow"

    registered_user = next(iter(persisted_users.values()))

    def _fake_current_user():
        return UserResponse(
            id_usuario=registered_user.id_usuario,
            email=registered_user.email,
            full_name=registered_user.full_name,
            rol=registered_user.rol,
            partner_id=registered_user.partner_id,
        )

    app.dependency_overrides = {}
    from api.dependencies.auth import get_current_user

    app.dependency_overrides[get_current_user] = _fake_current_user
    user_response = client.get(f"/auth/users/{registered_user.id_usuario}")

    assert user_response.status_code == 200
    assert user_response.json()["email"] == "flow@travelhub.com"
    assert user_response.json()["full_name"] == "Flow User"
    app.dependency_overrides = {}
