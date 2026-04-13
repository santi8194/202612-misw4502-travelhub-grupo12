import pytest
import sys
from pathlib import Path

BOOKING_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = BOOKING_ROOT.parent
for path in (str(BACKEND_ROOT), str(BOOKING_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from booking.api import create_app
import booking.config.uow as uow_mod


class DummyDespachador:
    def publicar_evento(self, evento, routing_key):
        return None

    def cerrar(self):
        return None


@pytest.fixture(autouse=True)
def disable_rabbitmq(monkeypatch):
    monkeypatch.setattr(uow_mod, 'DespachadorRabbitMQ', lambda *args, **kwargs: DummyDespachador())
    yield


@pytest.fixture
def app():
    app = create_app({'TESTING': True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()
