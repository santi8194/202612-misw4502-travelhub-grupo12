from types import SimpleNamespace
from datetime import datetime, timedelta
from uuid import uuid4

from infrastructure import database
from infrastructure.models import Role, User, UserSession


class DummySession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_get_db_yields_and_closes(monkeypatch):
    dummy = DummySession()
    monkeypatch.setattr("infrastructure.database.SessionLocal", lambda: dummy)

    generator = database.get_db()
    yielded = next(generator)
    assert yielded is dummy

    try:
        next(generator)
    except StopIteration:
        pass

    assert dummy.closed is True


def test_init_db_calls_create_all(monkeypatch):
    called = {"bind": None}

    def _fake_create_all(*, bind):
        called["bind"] = bind

    monkeypatch.setattr(database.Base.metadata, "create_all", _fake_create_all)

    database.init_db()

    assert called["bind"] is database.engine


def test_model_repr():
    role = Role(name="ADMIN_HOTEL")
    user = User(email="admin@travelhub.com", password_hash="hash")
    session = UserSession(
        id=uuid4(),
        user_id=uuid4(),
        refresh_token_hash="abc123",
        last_activity_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=1),
    )

    assert "ADMIN_HOTEL" in repr(role)
    assert "admin@travelhub.com" in repr(user)
    assert "UserSession" in repr(session)
