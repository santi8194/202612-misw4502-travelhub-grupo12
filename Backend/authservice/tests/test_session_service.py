from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from modules.session_service import SessionService


class FakeQuery:
    def __init__(self, result):
        self.result = result

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.result


class FakeSession:
    def __init__(self, query_result=None):
        self.query_result = query_result
        self.added = None
        self.commits = 0
        self.refreshed = []
        self.closed = False

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = uuid4()
        self.added = obj

    def commit(self):
        self.commits += 1

    def refresh(self, obj):
        self.refreshed.append(obj)

    def query(self, _model):
        return FakeQuery(self.query_result)

    def close(self):
        self.closed = True


def test_create_session_persists_refresh_token(monkeypatch):
    fake_db = FakeSession()
    user_id = uuid4()

    monkeypatch.setattr("modules.session_service.SessionLocal", lambda: fake_db)
    monkeypatch.setattr("modules.session_service.create_refresh_token", lambda: "refresh-123")
    monkeypatch.setattr("modules.session_service.hash_token", lambda token: f"hashed-{token}")

    session = SessionService.create_session(user_id)

    assert session.refresh_token == "refresh-123"
    assert fake_db.added.user_id == user_id
    assert fake_db.added.refresh_token_hash == "hashed-refresh-123"
    assert fake_db.commits == 1
    assert fake_db.closed is True


def test_validate_session_updates_last_activity(monkeypatch):
    stored_session = SimpleNamespace(
        id=uuid4(),
        user_id=uuid4(),
        last_activity_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=1),
        revoked_at=None,
        updated_at=datetime.utcnow(),
    )
    fake_db = FakeSession(query_result=stored_session)
    now = datetime.utcnow() + timedelta(minutes=1)

    monkeypatch.setattr("modules.session_service.SessionLocal", lambda: fake_db)
    monkeypatch.setattr("modules.session_service.SessionService._utcnow", lambda: now)

    is_valid = SessionService.validate_session(str(stored_session.id), stored_session.user_id, touch_activity=True)

    assert is_valid is True
    assert stored_session.last_activity_at == now
    assert fake_db.commits == 1


def test_rotate_refresh_token_rejects_inactive_session(monkeypatch):
    stored_session = SimpleNamespace(
        id=uuid4(),
        user_id=uuid4(),
        refresh_token_hash="hashed-refresh-old",
        last_activity_at=datetime.utcnow() - timedelta(hours=2),
        expires_at=datetime.utcnow() + timedelta(days=1),
        revoked_at=None,
        updated_at=datetime.utcnow(),
        user=SimpleNamespace(id=uuid4(), email="admin@travelhub.com", partner_id=None, roles=[]),
    )
    fake_db = FakeSession(query_result=stored_session)
    now = datetime.utcnow()

    monkeypatch.setattr("modules.session_service.SessionLocal", lambda: fake_db)
    monkeypatch.setattr("modules.session_service.SessionService._utcnow", lambda: now)
    monkeypatch.setattr("modules.session_service.hash_token", lambda token: f"hashed-{token}")

    rotated = SessionService.rotate_refresh_token("refresh-old")

    assert rotated is None
    assert stored_session.revoked_at == now
    assert fake_db.commits == 1


def test_rotate_refresh_token_returns_new_bundle(monkeypatch):
    user_id = uuid4()
    stored_session = SimpleNamespace(
        id=uuid4(),
        user_id=user_id,
        refresh_token_hash="hashed-refresh-old",
        last_activity_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=1),
        revoked_at=None,
        updated_at=datetime.utcnow(),
        user=SimpleNamespace(
            id=user_id,
            email="admin@travelhub.com",
            partner_id=None,
            roles=[SimpleNamespace(name="ADMIN_HOTEL")],
        ),
    )
    fake_db = FakeSession(query_result=stored_session)
    now = datetime.utcnow() + timedelta(minutes=1)

    monkeypatch.setattr("modules.session_service.SessionLocal", lambda: fake_db)
    monkeypatch.setattr("modules.session_service.SessionService._utcnow", lambda: now)
    monkeypatch.setattr("modules.session_service.hash_token", lambda token: f"hashed-{token}")
    monkeypatch.setattr("modules.session_service.create_refresh_token", lambda: "refresh-new")

    rotated = SessionService.rotate_refresh_token("refresh-old")

    assert rotated.refresh_token == "refresh-new"
    assert rotated.user_id == user_id
    assert rotated.email == "admin@travelhub.com"
    assert stored_session.refresh_token_hash == "hashed-refresh-new"
    assert stored_session.last_activity_at == now