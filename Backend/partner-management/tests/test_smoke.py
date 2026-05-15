"""
Comprehensive test suite for the PartnerManagement microservice.
Target: ≥ 80 % code coverage across all modules.
"""
import importlib
import json
import os

import pytest
import pika
import pika.exceptions
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_callback_mocks():
    ch = MagicMock()
    method = MagicMock()
    properties = MagicMock()
    return ch, method, properties


# ===========================================================================
# config/settings.py
# ===========================================================================

class TestSettings:
    def test_default_host(self):
        from config.settings import settings
        assert settings.RABBITMQ_HOST == "localhost"

    def test_default_port(self):
        from config.settings import settings
        assert settings.RABBITMQ_PORT == 5672

    def test_default_user(self):
        from config.settings import settings
        assert settings.RABBITMQ_USER == "guest"

    def test_default_pass(self):
        from config.settings import settings
        assert settings.RABBITMQ_PASS == "guest"

    def test_env_override(self):
        import config.settings as m
        with patch.dict(os.environ, {
            "RABBITMQ_HOST": "rabbithost",
            "RABBITMQ_PORT": "5000",
            "RABBITMQ_USER": "admin",
            "RABBITMQ_PASS": "secret",
        }):
            importlib.reload(m)
            assert m.settings.RABBITMQ_HOST == "rabbithost"
            assert m.settings.RABBITMQ_PORT == 5000
            assert m.settings.RABBITMQ_USER == "admin"
            assert m.settings.RABBITMQ_PASS == "secret"
        importlib.reload(m)  # restore defaults


# ===========================================================================
# config/rabbitmq.py
# ===========================================================================

class TestRabbitMQConnection:
    @patch("config.rabbitmq.pika.BlockingConnection")
    def test_succeeds_on_first_attempt(self, mock_bc):
        from config.rabbitmq import create_connection
        mock_conn = MagicMock()
        mock_bc.return_value = mock_conn
        assert create_connection(max_attempts=3, retry_delay=0) is mock_conn
        assert mock_bc.call_count == 1

    @patch("config.rabbitmq.time.sleep")
    @patch("config.rabbitmq.pika.BlockingConnection")
    def test_retries_on_amqp_error(self, mock_bc, mock_sleep):
        from config.rabbitmq import create_connection
        mock_conn = MagicMock()
        mock_bc.side_effect = [
            pika.exceptions.AMQPConnectionError(),
            pika.exceptions.AMQPConnectionError(),
            mock_conn,
        ]
        result = create_connection(max_attempts=5, retry_delay=1)
        assert result is mock_conn
        assert mock_bc.call_count == 3
        assert mock_sleep.call_count == 2

    @patch("config.rabbitmq.time.sleep")
    @patch("config.rabbitmq.pika.BlockingConnection")
    def test_exhausts_attempts_and_raises(self, mock_bc, mock_sleep):
        from config.rabbitmq import create_connection
        mock_bc.side_effect = pika.exceptions.AMQPConnectionError()
        with pytest.raises(Exception, match="Could not connect to RabbitMQ after retries"):
            create_connection(max_attempts=2, retry_delay=0)
        assert mock_bc.call_count == 2

    @patch("config.rabbitmq.time.sleep")
    @patch("config.rabbitmq.pika.BlockingConnection")
    def test_retry_delay_respected(self, mock_bc, mock_sleep):
        from config.rabbitmq import create_connection
        mock_conn = MagicMock()
        mock_bc.side_effect = [pika.exceptions.AMQPConnectionError(), mock_conn]
        create_connection(max_attempts=5, retry_delay=10)
        mock_sleep.assert_called_once_with(10)


# ===========================================================================
# config/app.py
# ===========================================================================

class TestCreateApp:
    def test_returns_fastapi_instance(self):
        from fastapi import FastAPI
        with patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.start_consumer"
        ):
            from config.app import create_app
            app = create_app()
        assert isinstance(app, FastAPI)

    def test_health_route_returns_ok(self):
        with patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.start_consumer"
        ):
            from config.app import create_app
            app = create_app()
            with TestClient(app) as client:
                resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_startup_creates_daemon_thread(self):
        # `threading` is imported *inside* create_app, so patch it at the
        # threading module level to intercept the Thread constructor.
        mock_t = MagicMock()
        with patch("threading.Thread", return_value=mock_t) as mock_thread, \
             patch(
                 "modules.partner.infrastructure.consumers"
                 ".solicitar_aprobacion_consumer.start_consumer"
             ):
            from config.app import create_app
            app = create_app()
            for handler in app.router.on_startup:
                handler()
        mock_thread.assert_called_once()
        assert mock_thread.call_args.kwargs.get("daemon") is True
        mock_t.start.assert_called_once()


# ===========================================================================
# publishers/aprobacion_publisher.py
# ===========================================================================

class TestPublishEvent:
    @patch(
        "modules.partner.infrastructure.publishers.aprobacion_publisher.create_connection"
    )
    def test_publishes_message(self, mock_cc):
        from modules.partner.infrastructure.publishers.aprobacion_publisher import publish_event
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_cc.return_value = mock_conn
        mock_conn.channel.return_value = mock_ch
        mock_conn.is_open = True

        publish_event("evt.test.key", "TestEvt", {"id_reserva": "r-1"})

        mock_ch.exchange_declare.assert_called_once_with(
            exchange="travelhub.events.exchange",
            exchange_type="topic",
            durable=True,
        )
        mock_ch.basic_publish.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch(
        "modules.partner.infrastructure.publishers.aprobacion_publisher.create_connection"
    )
    def test_message_fields(self, mock_cc):
        from modules.partner.infrastructure.publishers.aprobacion_publisher import publish_event
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_cc.return_value = mock_conn
        mock_conn.channel.return_value = mock_ch
        mock_conn.is_open = True

        publish_event("routing.key", "MyEvt", {"id_reserva": "r-2", "extra": "val"})

        body = json.loads(mock_ch.basic_publish.call_args.kwargs["body"])
        assert body["type"] == "MyEvt"
        assert body["id_reserva"] == "r-2"
        assert body["extra"] == "val"

    @patch(
        "modules.partner.infrastructure.publishers.aprobacion_publisher.create_connection"
    )
    def test_delivery_mode_persistent(self, mock_cc):
        from modules.partner.infrastructure.publishers.aprobacion_publisher import publish_event
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_cc.return_value = mock_conn
        mock_conn.channel.return_value = mock_ch
        mock_conn.is_open = True

        publish_event("rk", "Evt", {"id_reserva": "r-3"})

        props = mock_ch.basic_publish.call_args.kwargs["properties"]
        assert props.delivery_mode == 2

    @patch(
        "modules.partner.infrastructure.publishers.aprobacion_publisher.create_connection"
    )
    def test_exception_is_caught_and_connection_closed(self, mock_cc):
        from modules.partner.infrastructure.publishers.aprobacion_publisher import publish_event
        mock_conn = MagicMock()
        mock_conn.is_open = True
        mock_conn.channel.side_effect = RuntimeError("channel error")
        mock_cc.return_value = mock_conn

        publish_event("rk", "Evt", {"id_reserva": "r-err"})  # must not raise

        mock_conn.close.assert_called_once()

    @patch(
        "modules.partner.infrastructure.publishers.aprobacion_publisher.create_connection"
    )
    def test_create_connection_fails_no_close(self, mock_cc):
        from modules.partner.infrastructure.publishers.aprobacion_publisher import publish_event
        mock_cc.side_effect = RuntimeError("no connection")
        # connection is None; must not raise
        publish_event("rk", "Evt", {"id_reserva": "r-none"})


class TestPublishReservaAprobada:
    @patch(
        "modules.partner.infrastructure.publishers.aprobacion_publisher.publish_event"
    )
    def test_calls_publish_event_with_correct_args(self, mock_pe):
        from modules.partner.infrastructure.publishers.aprobacion_publisher import (
            publish_reserva_aprobada,
        )
        publish_reserva_aprobada("res-abc")
        mock_pe.assert_called_once_with(
            routing_key="evt.partnermanagement.reserva-aprobada",
            event_type="ReservaAprobadaManualEvt",
            data={"id_reserva": "res-abc"},
        )


class TestPublishReservaRechazada:
    @patch(
        "modules.partner.infrastructure.publishers.aprobacion_publisher.publish_event"
    )
    def test_calls_publish_event_with_correct_args(self, mock_pe):
        from modules.partner.infrastructure.publishers.aprobacion_publisher import (
            publish_reserva_rechazada,
        )
        publish_reserva_rechazada("res-xyz", "motivo de rechazo")
        mock_pe.assert_called_once_with(
            routing_key="evt.partnermanagement.reserva-rechazada",
            event_type="ReservaRechazadaManualEvt",
            data={"id_reserva": "res-xyz", "motivo": "motivo de rechazo"},
        )


# ===========================================================================
# consumers/solicitar_aprobacion_consumer.py – callback
# ===========================================================================

class TestConsumerCallback:
    def test_approves_when_random_below_threshold(self):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import callback
        ch, method, props = _make_callback_mocks()
        body = json.dumps({"commandType": "SolicitarAprobacionManualCmd", "id_reserva": "r-1"}).encode()

        with patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.random.random",
            return_value=0.5,
        ), patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.publish_reserva_aprobada"
        ) as mock_aprobada, patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.publish_reserva_rechazada"
        ) as mock_rechazada:
            callback(ch, method, props, body)

        mock_aprobada.assert_called_once_with("r-1")
        mock_rechazada.assert_not_called()
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)

    def test_rejects_when_random_above_threshold(self):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import callback
        ch, method, props = _make_callback_mocks()
        body = json.dumps({"commandType": "SolicitarAprobacionManualCmd", "id_reserva": "r-2"}).encode()

        with patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.random.random",
            return_value=0.9,
        ), patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.publish_reserva_aprobada"
        ) as mock_aprobada, patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.publish_reserva_rechazada"
        ) as mock_rechazada:
            callback(ch, method, props, body)

        mock_rechazada.assert_called_once_with("r-2", "El cliente está reportado negativamente")
        mock_aprobada.assert_not_called()
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)

    def test_uses_type_key_when_commandType_absent(self):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import callback
        ch, method, props = _make_callback_mocks()
        body = json.dumps({"type": "SolicitarAprobacionManual", "id_reserva": "r-3"}).encode()

        with patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.random.random",
            return_value=0.1,
        ), patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.publish_reserva_aprobada"
        ) as mock_aprobada:
            callback(ch, method, props, body)

        mock_aprobada.assert_called_once_with("r-3")

    def test_falls_back_to_reservaId_key(self):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import callback
        ch, method, props = _make_callback_mocks()
        body = json.dumps({"commandType": "Cmd", "reservaId": "r-fallback"}).encode()

        with patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.random.random",
            return_value=0.1,
        ), patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.publish_reserva_aprobada"
        ) as mock_aprobada:
            callback(ch, method, props, body)

        mock_aprobada.assert_called_once_with("r-fallback")

    def test_invalid_json_is_caught(self):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import callback
        ch, method, props = _make_callback_mocks()
        callback(ch, method, props, b"not-json")  # must not raise

    def test_exception_during_publish_is_caught(self):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import callback
        ch, method, props = _make_callback_mocks()
        body = json.dumps({"commandType": "Cmd", "id_reserva": "r-5"}).encode()

        with patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.random.random",
            return_value=0.1,
        ), patch(
            "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.publish_reserva_aprobada",
            side_effect=RuntimeError("publish error"),
        ):
            callback(ch, method, props, body)  # must not raise

    def test_exception_prints_error_message(self, capsys):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import callback
        ch, method, props = _make_callback_mocks()
        callback(ch, method, props, b"bad-json")
        out = capsys.readouterr().out
        assert "Error procesando comando" in out


# ===========================================================================
# consumers/solicitar_aprobacion_consumer.py – _configure_consumer_channel
# ===========================================================================

class TestConfigureConsumerChannel:
    def test_exchange_declared(self):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import (
            _configure_consumer_channel,
        )
        ch = MagicMock()
        _configure_consumer_channel(ch)
        ch.exchange_declare.assert_called_once_with(
            exchange="travelhub.commands.exchange",
            exchange_type="direct",
            durable=True,
        )

    def test_queue_declared(self):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import (
            _configure_consumer_channel,
        )
        ch = MagicMock()
        _configure_consumer_channel(ch)
        ch.queue_declare.assert_called_once_with(
            queue="partnermanagement.commands.queue",
            durable=True,
        )

    def test_queue_bound(self):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import (
            _configure_consumer_channel,
        )
        ch = MagicMock()
        _configure_consumer_channel(ch)
        ch.queue_bind.assert_called_once_with(
            exchange="travelhub.commands.exchange",
            queue="partnermanagement.commands.queue",
            routing_key="cmd.partnermanagement.solicitar-aprobacion",
        )

    def test_basic_consume_auto_ack_false(self):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import (
            _configure_consumer_channel,
        )
        ch = MagicMock()
        _configure_consumer_channel(ch)
        kw = ch.basic_consume.call_args.kwargs
        assert kw.get("queue") == "partnermanagement.commands.queue"
        assert kw.get("auto_ack") is False


# ===========================================================================
# consumers/solicitar_aprobacion_consumer.py – start_consumer
# ===========================================================================

class TestStartConsumer:
    @staticmethod
    def _raise_after(n, exc_type=KeyboardInterrupt):
        counter = [0]
        def _side_effect(*args, **kwargs):
            counter[0] += 1
            if counter[0] > n:
                raise exc_type("stop test")
            raise pika.exceptions.AMQPConnectionError("no rabbit")
        return _side_effect

    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.time.sleep"
    )
    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.create_connection"
    )
    def test_reconnects_after_connection_error(self, mock_cc, mock_sleep):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import start_consumer
        mock_cc.side_effect = self._raise_after(1)
        with pytest.raises(KeyboardInterrupt):
            start_consumer()
        assert mock_cc.call_count == 2
        mock_sleep.assert_called()

    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.time.sleep"
    )
    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer._configure_consumer_channel"
    )
    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.create_connection"
    )
    def test_closes_channel_and_connection_in_finally(self, mock_cc, mock_cfg, mock_sleep):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import start_consumer
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_conn.channel.return_value = mock_ch
        mock_conn.is_open = True
        mock_ch.is_open = True
        mock_ch.start_consuming.side_effect = Exception("stop consuming")

        calls = [0]
        def _side_effect(*a, **kw):
            calls[0] += 1
            if calls[0] >= 2:
                raise KeyboardInterrupt()
            return mock_conn

        mock_cc.side_effect = _side_effect
        with pytest.raises(KeyboardInterrupt):
            start_consumer()

        mock_ch.close.assert_called()
        mock_conn.close.assert_called()

    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.time.sleep"
    )
    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer._configure_consumer_channel"
    )
    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.create_connection"
    )
    def test_prints_reconnect_message_when_consuming_stops(self, mock_cc, mock_cfg, mock_sleep, capsys):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import start_consumer
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_conn.channel.return_value = mock_ch
        mock_ch.start_consuming.return_value = None  # returns normally

        calls = [0]
        def _side_effect(*a, **kw):
            calls[0] += 1
            if calls[0] >= 2:
                raise KeyboardInterrupt()
            return mock_conn

        mock_cc.side_effect = _side_effect
        with pytest.raises(KeyboardInterrupt):
            start_consumer()

        out = capsys.readouterr().out
        assert "Consumer stopped" in out or "reconnecting" in out.lower()

    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.time.sleep"
    )
    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer._configure_consumer_channel"
    )
    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.create_connection"
    )
    def test_swallows_exceptions_during_close(self, mock_cc, mock_cfg, mock_sleep):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import start_consumer
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_conn.channel.return_value = mock_ch
        mock_conn.is_open = True
        mock_ch.is_open = True
        mock_ch.start_consuming.side_effect = Exception("stop")
        mock_ch.close.side_effect = Exception("close ch failed")
        mock_conn.close.side_effect = Exception("close conn failed")

        calls = [0]
        def _side_effect(*a, **kw):
            calls[0] += 1
            if calls[0] >= 2:
                raise KeyboardInterrupt()
            return mock_conn

        mock_cc.side_effect = _side_effect
        with pytest.raises(KeyboardInterrupt):
            start_consumer()  # close exceptions must not propagate

    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.time.sleep"
    )
    @patch(
        "modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer.create_connection"
    )
    def test_finally_handles_none_channel_and_connection(self, mock_cc, mock_sleep):
        from modules.partner.infrastructure.consumers.solicitar_aprobacion_consumer import start_consumer
        mock_cc.side_effect = self._raise_after(1)
        with pytest.raises(KeyboardInterrupt):
            start_consumer()

