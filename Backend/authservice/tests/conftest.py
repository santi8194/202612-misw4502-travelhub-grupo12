from uuid import uuid4

import pytest

from data.user import UserInDB
from modules import auth_service


@pytest.fixture(autouse=True)
def clear_failed_logins() -> None:
    auth_service._failed_logins.clear()
    yield
    auth_service._failed_logins.clear()


@pytest.fixture
def sample_user() -> UserInDB:
    return UserInDB(
        id_usuario=uuid4(),
        email="admin@travelhub.com",
        password_hash="$2b$12$YylAfb54R4zu5Kz1ZwM.5e6nPj4kAN6rA3Q0jVQbghCvxGf7z8h2y",  # hash for "123456"
        rol="ADMIN_HOTEL",
        partner_id=None,
    )
