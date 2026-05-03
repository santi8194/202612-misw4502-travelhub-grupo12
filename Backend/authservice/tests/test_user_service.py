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


def test_get_user_by_id_with_role(monkeypatch):
    user_id = uuid4()
    partner_id = uuid4()
    fake_user = SimpleNamespace(
        id=user_id,
        email="guest@travelhub.com",
        password_hash="hashed",
        full_name="Guest User",
        roles=[SimpleNamespace(name="USER")],
        partner_id=partner_id,
    )
    fake_session = FakeSession(result=fake_user)
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: fake_session)

    user = UserService.get_user_by_id(user_id)

    assert user is not None
    assert user.id_usuario == user_id
    assert user.email == "guest@travelhub.com"
    assert user.full_name == "Guest User"
    assert user.partner_id == partner_id
    assert user.rol == "USER"
    assert fake_session.closed is True


def test_get_user_by_id_not_found(monkeypatch):
    fake_session = FakeSession(result=None)
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: fake_session)

    user = UserService.get_user_by_id(uuid4())

    assert user is None
    assert fake_session.closed is True


def test_get_user_by_id_handles_exception(monkeypatch):
    fake_session = FakeSession(error=RuntimeError("db error"))
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: fake_session)

    user = UserService.get_user_by_id(uuid4())

    assert user is None
    assert fake_session.closed is True


# ---------------------------------------------------------------------------
# MutableFakeSession: supports add/commit/rollback for write operations
# ---------------------------------------------------------------------------

class MutableFakeQuery:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        if self.error:
            raise self.error
        return self.result


class MutableFakeSession:
    def __init__(self, results_by_model=None, commit_error=None):
        self._results = results_by_model or {}
        self._commit_error = commit_error
        self.closed = False
        self.added = []
        self.committed = False
        self.rolled_back = False

    def query(self, model):
        model_name = getattr(model, "__name__", str(model))
        result = self._results.get(model_name)
        return MutableFakeQuery(result)

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        pass

    def commit(self):
        if self._commit_error:
            raise self._commit_error
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def refresh(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = uuid4()

    def close(self):
        self.closed = True


# ---------------------------------------------------------------------------
# get_user_by_username tests
# ---------------------------------------------------------------------------

def test_get_user_by_username_with_role(monkeypatch):
    partner_id = uuid4()
    fake_user = SimpleNamespace(
        id=uuid4(),
        email="admin@travelhub.com",
        password_hash="hashed",
        username="cognito-sub-123",
        roles=[SimpleNamespace(name="ADMIN_HOTEL")],
        partner_id=partner_id,
    )
    fake_session = FakeSession(result=fake_user)
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: fake_session)

    user = UserService.get_user_by_username("cognito-sub-123")

    assert user is not None
    assert user.email == "admin@travelhub.com"
    assert user.rol == "ADMIN_HOTEL"
    assert user.partner_id == partner_id
    assert fake_session.closed is True


def test_get_user_by_username_not_found(monkeypatch):
    fake_session = FakeSession(result=None)
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: fake_session)

    user = UserService.get_user_by_username("nonexistent-sub")

    assert user is None
    assert fake_session.closed is True


def test_get_user_by_username_handles_exception(monkeypatch):
    fake_session = FakeSession(error=RuntimeError("db error"))
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: fake_session)

    user = UserService.get_user_by_username("some-sub")

    assert user is None
    assert fake_session.closed is True


# ---------------------------------------------------------------------------
# create_or_update_registered_user tests
# ---------------------------------------------------------------------------

def test_create_or_update_registered_user_creates_new(monkeypatch):
    session = MutableFakeSession(results_by_model={"User": None, "Role": None})
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: session)

    result = UserService.create_or_update_registered_user(
        email="new@travelhub.com",
        full_name="New User",
        username="cognito-sub-new",
        active=False,
    )

    assert result is not None
    assert result.email == "new@travelhub.com"
    assert result.rol == "USER"
    assert len(session.added) == 1
    assert session.committed is True
    assert session.closed is True


def test_create_or_update_registered_user_updates_existing(monkeypatch):
    existing_user = SimpleNamespace(
        id=uuid4(),
        email="existing@travelhub.com",
        username="old-sub",
        full_name="Old Name",
        password_hash="OLD_HASH",
        is_active="false",
        roles=[SimpleNamespace(name="ADMIN_HOTEL")],
        partner_id=None,
        updated_at=None,
    )
    session = MutableFakeSession(results_by_model={"User": existing_user, "Role": None})
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: session)

    result = UserService.create_or_update_registered_user(
        email="existing@travelhub.com",
        full_name="New Name",
        username="new-sub",
        active=True,
    )

    assert result is not None
    assert existing_user.username == "new-sub"
    assert existing_user.full_name == "New Name"
    assert existing_user.is_active == "true"
    assert result.rol == "ADMIN_HOTEL"
    assert session.committed is True
    assert session.closed is True


def test_create_or_update_registered_user_exception(monkeypatch):
    session = MutableFakeSession(
        results_by_model={"User": None, "Role": None},
        commit_error=RuntimeError("db error"),
    )
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: session)

    result = UserService.create_or_update_registered_user(
        email="error@travelhub.com",
        full_name="Error User",
        username="error-sub",
        active=False,
    )

    assert result is None
    assert session.rolled_back is True
    assert session.closed is True


# ---------------------------------------------------------------------------
# activate_user tests
# ---------------------------------------------------------------------------

def test_activate_user_success(monkeypatch):
    fake_user = SimpleNamespace(
        id=uuid4(),
        email="user@travelhub.com",
        is_active="false",
        updated_at=None,
    )
    session = MutableFakeSession(results_by_model={"User": fake_user})
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: session)

    result = UserService.activate_user("user@travelhub.com")

    assert result is True
    assert fake_user.is_active == "true"
    assert session.committed is True
    assert session.closed is True


def test_activate_user_not_found(monkeypatch):
    session = MutableFakeSession(results_by_model={"User": None})
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: session)

    result = UserService.activate_user("missing@travelhub.com")

    assert result is False
    assert session.closed is True


def test_activate_user_exception(monkeypatch):
    fake_user = SimpleNamespace(
        id=uuid4(),
        email="user@travelhub.com",
        is_active="false",
        updated_at=None,
    )
    session = MutableFakeSession(
        results_by_model={"User": fake_user},
        commit_error=RuntimeError("db error"),
    )
    monkeypatch.setattr("modules.user_service.SessionLocal", lambda: session)

    result = UserService.activate_user("user@travelhub.com")

    assert result is False
    assert session.rolled_back is True
    assert session.closed is True
