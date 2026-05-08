from types import SimpleNamespace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure import database
from infrastructure.database import Base
from infrastructure.models import Role, User, UserSession


def _make_in_memory_sessionmaker():
    """Creates a fresh in-memory SQLite session factory with all tables."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


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
    seeded = {"called": False}

    def _fake_create_all(*, bind):
        called["bind"] = bind

    def _fake_seed_sqlite_defaults():
        seeded["called"] = True

    monkeypatch.setattr(database.Base.metadata, "create_all", _fake_create_all)
    monkeypatch.setattr(database, "_seed_sqlite_defaults", _fake_seed_sqlite_defaults)
    monkeypatch.setattr(database, "IS_SQLITE", False)

    database.init_db()

    assert called["bind"] is database.engine
    assert seeded["called"] is False


def test_model_repr():
    role = Role(name="ADMIN_HOTEL")
    user = User(email="admin@travelhub.com", password_hash="hash")
    session = UserSession(
        id=uuid4(),
        user_id=uuid4(),
        refresh_token_hash="abc123",
        last_activity_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )

    assert "ADMIN_HOTEL" in repr(role)
    assert "admin@travelhub.com" in repr(user)
    assert "UserSession" in repr(session)


# ---------------------------------------------------------------------------
# _seed_sqlite_defaults tests (real in-memory SQLite)
# ---------------------------------------------------------------------------

def test_seed_sqlite_defaults_populates_empty_db(monkeypatch):
    TestSession = _make_in_memory_sessionmaker()
    monkeypatch.setattr(database, "SessionLocal", TestSession)

    database._seed_sqlite_defaults()

    db = TestSession()
    try:
        roles = db.query(Role).all()
        users = db.query(User).all()
        assert len(roles) == 2
        assert {r.name for r in roles} == {"ADMIN_HOTEL", "USER"}
        assert len(users) == 3
    finally:
        db.close()


def test_seed_sqlite_defaults_idempotent(monkeypatch):
    """Running seed twice must not duplicate roles or users."""
    TestSession = _make_in_memory_sessionmaker()
    monkeypatch.setattr(database, "SessionLocal", TestSession)

    database._seed_sqlite_defaults()
    database._seed_sqlite_defaults()

    db = TestSession()
    try:
        assert db.query(Role).count() == 2
        assert db.query(User).count() == 3
    finally:
        db.close()


# ---------------------------------------------------------------------------
# init_db with IS_SQLITE=True test
# ---------------------------------------------------------------------------

def test_init_db_is_sqlite_calls_seed(monkeypatch):
    seeded = {"called": False}

    def _fake_create_all(*, bind):
        pass

    def _fake_seed_sqlite_defaults():
        seeded["called"] = True

    monkeypatch.setattr(database.Base.metadata, "create_all", _fake_create_all)
    monkeypatch.setattr(database, "_seed_sqlite_defaults", _fake_seed_sqlite_defaults)
    monkeypatch.setattr(database, "IS_SQLITE", True)

    database.init_db()

    assert seeded["called"] is True
