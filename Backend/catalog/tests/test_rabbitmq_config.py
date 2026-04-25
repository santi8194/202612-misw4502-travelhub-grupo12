from config import rabbitmq as rabbitmq_module


def test_create_connection_success_on_first_attempt(monkeypatch, capsys):
    monkeypatch.setattr(rabbitmq_module.settings, "RABBITMQ_USER", "guest")
    monkeypatch.setattr(rabbitmq_module.settings, "RABBITMQ_PASS", "guest")
    monkeypatch.setattr(rabbitmq_module.settings, "RABBITMQ_HOST", "localhost")
    monkeypatch.setattr(rabbitmq_module.settings, "RABBITMQ_PORT", 5672)

    recorded = {}
    fake_connection = object()

    class FakePika:
        class exceptions:
            AMQPConnectionError = RuntimeError

        @staticmethod
        def PlainCredentials(user, password):
            recorded["credentials"] = (user, password)
            return (user, password)

        @staticmethod
        def ConnectionParameters(host, port, credentials):
            recorded["parameters"] = {
                "host": host,
                "port": port,
                "credentials": credentials,
            }
            return recorded["parameters"]

        @staticmethod
        def BlockingConnection(parameters):
            recorded["blocking_connection_parameters"] = parameters
            return fake_connection

    monkeypatch.setattr(rabbitmq_module, "pika", FakePika)

    connection = rabbitmq_module.create_connection()

    assert connection is fake_connection
    assert recorded["credentials"] == ("guest", "guest")
    assert recorded["parameters"]["host"] == "localhost"
    assert recorded["parameters"]["port"] == 5672
    assert "Connecting to RabbitMQ (attempt 1)" in capsys.readouterr().out


def test_create_connection_raises_after_all_retries(monkeypatch, capsys):
    monkeypatch.setattr(rabbitmq_module.settings, "RABBITMQ_USER", "guest")
    monkeypatch.setattr(rabbitmq_module.settings, "RABBITMQ_PASS", "guest")
    monkeypatch.setattr(rabbitmq_module.settings, "RABBITMQ_HOST", "localhost")
    monkeypatch.setattr(rabbitmq_module.settings, "RABBITMQ_PORT", 5672)

    recorded = {"attempts": 0, "sleeps": []}

    amqp_connection_error = type("AMQPConnectionError", (Exception,), {})

    class FakePika:
        class exceptions:
            AMQPConnectionError = amqp_connection_error

        @staticmethod
        def PlainCredentials(user, password):
            return (user, password)

        @staticmethod
        def ConnectionParameters(host, port, credentials):
            return {
                "host": host,
                "port": port,
                "credentials": credentials,
            }

        @staticmethod
        def BlockingConnection(parameters):
            recorded["attempts"] += 1
            raise amqp_connection_error("not ready")

    monkeypatch.setattr(rabbitmq_module, "pika", FakePika)
    monkeypatch.setattr(rabbitmq_module.time, "sleep", lambda seconds: recorded["sleeps"].append(seconds))

    try:
        rabbitmq_module.create_connection()
        assert False, "Expected create_connection to raise after retries"
    except Exception as exc:
        assert str(exc) == "Could not connect to RabbitMQ after retries"

    output = capsys.readouterr().out
    assert recorded["attempts"] == 10
    assert len(recorded["sleeps"]) == 10
    assert all(seconds == 5 for seconds in recorded["sleeps"])
    assert "retrying in 5 seconds" in output