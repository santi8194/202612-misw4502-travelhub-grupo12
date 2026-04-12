from types import SimpleNamespace
from uuid import uuid4

from modules.user_service import UserService


class FakeQuery:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        if self.error:
            raise self.error
        return self.result


class FakeSession:
    def __init__(self, result=None, error=None):
        self._result = result
        self._error = error
        self.closed = False

    def query(self, *_args, **_kwargs):
        return FakeQuery(self._result, self._error)

    def close(self):
        self.closed = True


def test_get_user_by_email_with_role(monkeypatch):
    partner_id = uuid4()
    fake_user = SimpleNamespace(
        id=uuid4(),
        email="admin@travelhub.com",
        password_hash="hashed",
        roles=[SimpleNamespace(name="ADMIN_HOTEL")],
        partner_id=partner_id,
    )
    fake_session = FakeSession(result=fake_user)
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: fake_session)

    user = UserService.get_user_by_email("admin@travelhub.com")

    assert user is not None
    assert user.rol == "ADMIN_HOTEL"
    assert user.partner_id == partner_id
    assert fake_session.closed is True


def test_get_user_by_email_without_roles_defaults_user(monkeypatch):
    fake_user = SimpleNamespace(
        id=uuid4(),
        email="user@travelhub.com",
        password_hash="hashed",
        roles=[],
        partner_id=None,
    )
    fake_session = FakeSession(result=fake_user)
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: fake_session)

    user = UserService.get_user_by_email("user@travelhub.com")

    assert user is not None
    assert user.rol == "USER"


def test_get_user_by_email_not_found(monkeypatch):
    fake_session = FakeSession(result=None)
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: fake_session)

    user = UserService.get_user_by_email("missing@travelhub.com")

    assert user is None
    assert fake_session.closed is True


def test_get_user_by_email_handles_exception(monkeypatch):
    fake_session = FakeSession(error=RuntimeError("db error"))
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: fake_session)

    user = UserService.get_user_by_email("error@travelhub.com")

    assert user is None
    assert fake_session.closed is True
