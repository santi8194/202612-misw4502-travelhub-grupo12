import pytest
from booking.api import create_app
import config.uow as uow_mod


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
