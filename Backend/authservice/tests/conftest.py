from uuid import uuid4

import pytest

from data.user import UserInDB


@pytest.fixture
def sample_user() -> UserInDB:
    return UserInDB(
        id_usuario=uuid4(),
        email="admin@travelhub.com",
        rol="ADMIN_HOTEL",
        partner_id=None,
    )


@pytest.fixture
def cognito_auth_result() -> dict:
    """Simula el AuthenticationResult de Cognito."""
    return {
        "AccessToken": "fake-access-token",
        "IdToken": "fake-id-token",
        "RefreshToken": "fake-refresh-token",
        "ExpiresIn": 3600,
        "TokenType": "Bearer",
    }


@pytest.fixture
def cognito_refresh_result() -> dict:
    """Simula el AuthenticationResult de un REFRESH_TOKEN_AUTH (sin RefreshToken nuevo)."""
    return {
        "AccessToken": "new-access-token",
        "IdToken": "new-id-token",
        "ExpiresIn": 3600,
        "TokenType": "Bearer",
    }
