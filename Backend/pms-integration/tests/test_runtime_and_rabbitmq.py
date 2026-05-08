import main as main_module
from config import rabbitmq as rabbitmq_module
from modules.pms.infrastructure.services import event_bus as event_bus_module


def test_startup_starts_consumer_thread(monkeypatch):
    state = {}

    class FakeThread:
        def __init__(self, target):
            state["target"] = target
            self.daemon = False

        def start(self):
            state["started"] = True
            state["daemon"] = self.daemon

    monkeypatch.setattr(main_module.threading, "Thread", FakeThread)

    main_module.start_rabbitmq_consumer()

    assert state["target"] is main_module.start_consumer
    assert state["started"] is True
    assert state["daemon"] is True


def test_event_bus_publishes_and_closes_connection(monkeypatch):
    recorded = {}

    class FakeChannel:
        def exchange_declare(self, **kwargs):
            recorded.setdefault("exchange_calls", []).append(kwargs)

        def basic_publish(self, **kwargs):
            recorded["publish"] = kwargs

    class FakeConnection:
        is_open = True

        def channel(self):
            return FakeChannel()

        def close(self):
            recorded["closed"] = True

    monkeypatch.setattr(event_bus_module, "create_connection", lambda: FakeConnection())

    event_bus_module.EventBus().publish_event("evt.test", "EvtTest", {"k": "v"})

    assert len(recorded["exchange_calls"]) == 2
    assert recorded["publish"]["routing_key"] == "evt.test"
    assert recorded["closed"] is True


def test_rabbitmq_create_connection_success(monkeypatch):
    fake_connection = object()

    class FakePika:
        class exceptions:
            AMQPConnectionError = RuntimeError

        @staticmethod
        def PlainCredentials(user, password):
            return (user, password)

        @staticmethod
        def ConnectionParameters(host, port, credentials):
            return (host, port, credentials)

        @staticmethod
        def BlockingConnection(parameters):
            return fake_connection

    monkeypatch.setattr(rabbitmq_module, "pika", FakePika)

    conn = rabbitmq_module.create_connection()

    assert conn is fake_connection


def test_rabbitmq_create_connection_retries_and_fails(monkeypatch):
    attempts = {"count": 0}
    sleeps = []
    amqp_error = type("AMQPConnectionError", (Exception,), {})

    class FakePika:
        class exceptions:
            AMQPConnectionError = amqp_error

        @staticmethod
        def PlainCredentials(user, password):
            return (user, password)

        @staticmethod
        def ConnectionParameters(host, port, credentials):
            return (host, port, credentials)

        @staticmethod
        def BlockingConnection(parameters):
            attempts["count"] += 1
            raise amqp_error("not ready")

    monkeypatch.setattr(rabbitmq_module, "pika", FakePika)
    monkeypatch.setattr(rabbitmq_module.time, "sleep", lambda s: sleeps.append(s))

    try:
        rabbitmq_module.create_connection()
        assert False, "Expected create_connection to fail after retries"
    except Exception as exc:
        assert str(exc) == "Could not connect to RabbitMQ after retries"

    assert attempts["count"] == 10
    assert len(sleeps) == 10


def test_rabbitmq_create_connection_unlimited_retries_until_success(monkeypatch):
    attempts = {"count": 0}
    sleeps = []
    amqp_error = type("AMQPConnectionError", (Exception,), {})
    fake_connection = object()

    class FakePika:
        class exceptions:
            AMQPConnectionError = amqp_error

        @staticmethod
        def PlainCredentials(user, password):
            return (user, password)

        @staticmethod
        def ConnectionParameters(host, port, credentials):
            return (host, port, credentials)

        @staticmethod
        def BlockingConnection(parameters):
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise amqp_error("not ready")
            return fake_connection

    monkeypatch.setattr(rabbitmq_module, "pika", FakePika)
    monkeypatch.setattr(rabbitmq_module.time, "sleep", lambda s: sleeps.append(s))

    conn = rabbitmq_module.create_connection(max_attempts=None, retry_delay=5)

    assert conn is fake_connection
    assert attempts["count"] == 3
    assert sleeps == [5, 5]
