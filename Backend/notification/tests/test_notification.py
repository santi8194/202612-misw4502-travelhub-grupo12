
"""
Comprehensive test suite for the Notification microservice.
Target: ≥ 80 % code coverage across all modules.
"""
import importlib
import json
import os
import sys

import pytest
import pika
import pika.exceptions
from unittest import mock
from unittest.mock import MagicMock, call, patch
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
# api/health.py
# ===========================================================================

class TestHealthEndpoint:
    """Tests for the /health route."""

    def test_health_returns_200(self):
        # Keep the patch active through TestClient startup so the daemon
        # thread uses the mock and does not attempt a real RabbitMQ connection.
        with patch("config.app.start_consumer"):
            from config.app import create_app
            app = create_app()
            with TestClient(app) as client:
                resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_response_body(self):
        with patch("config.app.start_consumer"):
            from config.app import create_app
            app = create_app()
            with TestClient(app) as client:
                resp = client.get("/health")
        assert resp.json() == {"status": "Notification Service running"}


# ===========================================================================
# config/settings.py
# ===========================================================================

class TestSettings:
    """Tests for the Settings configuration class."""

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
            "RABBITMQ_HOST": "myhost",
            "RABBITMQ_PORT": "5673",
            "RABBITMQ_USER": "admin",
            "RABBITMQ_PASS": "s3cr3t",
        }):
            importlib.reload(m)
            assert m.settings.RABBITMQ_HOST == "myhost"
            assert m.settings.RABBITMQ_PORT == 5673
            assert m.settings.RABBITMQ_USER == "admin"
            assert m.settings.RABBITMQ_PASS == "s3cr3t"
        # Restore defaults for other tests
        importlib.reload(m)


# ===========================================================================
# config/rabbitmq.py
# ===========================================================================

class TestRabbitMQConnection:
    """Tests for create_connection retry logic."""

    @patch("config.rabbitmq.pika.BlockingConnection")
    def test_succeeds_on_first_attempt(self, mock_bc):
        from config.rabbitmq import create_connection
        mock_conn = MagicMock()
        mock_bc.return_value = mock_conn

        result = create_connection(max_attempts=3, retry_delay=0)

        assert result is mock_conn
        assert mock_bc.call_count == 1

    @patch("config.rabbitmq.time.sleep")
    @patch("config.rabbitmq.pika.BlockingConnection")
    def test_retries_then_succeeds(self, mock_bc, mock_sleep):
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
    def test_exhausts_attempts_raises(self, mock_bc, mock_sleep):
        from config.rabbitmq import create_connection
        mock_bc.side_effect = pika.exceptions.AMQPConnectionError()

        with pytest.raises(Exception, match="Could not connect to RabbitMQ after retries"):
            create_connection(max_attempts=3, retry_delay=0)

        assert mock_bc.call_count == 3

    @patch("config.rabbitmq.time.sleep")
    @patch("config.rabbitmq.pika.BlockingConnection")
    def test_retry_delay_is_used(self, mock_bc, mock_sleep):
        from config.rabbitmq import create_connection
        mock_conn = MagicMock()
        mock_bc.side_effect = [pika.exceptions.AMQPConnectionError(), mock_conn]

        create_connection(max_attempts=5, retry_delay=7)

        mock_sleep.assert_called_once_with(7)


# ===========================================================================
# modules/services/email_service.py
# ===========================================================================

class TestEmailService:
    """Tests for send_voucher_email."""

    def test_returns_true(self):
        from modules.services.email_service import send_voucher_email
        assert send_voucher_email("test@example.com", "res-123") is True

    def test_prints_email_and_reservation(self, capsys):
        from modules.services.email_service import send_voucher_email
        send_voucher_email("user@mail.com", "res-456")
        out = capsys.readouterr().out
        assert "user@mail.com" in out
        assert "res-456" in out


# ===========================================================================
# modules/publishers/voucher_enviado_publisher.py
# ===========================================================================

class TestVoucherEnviadoPublisher:
    """Tests for publish_voucher_enviado."""

    @patch("modules.publishers.voucher_enviado_publisher.pika.BlockingConnection")
    def test_declares_exchange_and_publishes(self, mock_bc):
        from modules.publishers.voucher_enviado_publisher import publish_voucher_enviado
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_bc.return_value = mock_conn
        mock_conn.channel.return_value = mock_ch

        publish_voucher_enviado("res-789")

        mock_ch.exchange_declare.assert_called_once_with(
            exchange="travelhub.events.exchange",
            exchange_type="topic",
            durable=True,
        )
        mock_ch.basic_publish.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("modules.publishers.voucher_enviado_publisher.pika.BlockingConnection")
    def test_event_body_fields(self, mock_bc):
        from modules.publishers.voucher_enviado_publisher import publish_voucher_enviado
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_bc.return_value = mock_conn
        mock_conn.channel.return_value = mock_ch

        publish_voucher_enviado("res-001")

        body = json.loads(mock_ch.basic_publish.call_args.kwargs["body"])
        assert body["type"] == "VoucherEnviadoEvt"
        assert body["id_reserva"] == "res-001"
        assert body["status"] == "ENVIADO"

    @patch("modules.publishers.voucher_enviado_publisher.pika.BlockingConnection")
    def test_routing_key_and_exchange(self, mock_bc):
        from modules.publishers.voucher_enviado_publisher import publish_voucher_enviado
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_bc.return_value = mock_conn
        mock_conn.channel.return_value = mock_ch

        publish_voucher_enviado("res-002")

        kw = mock_ch.basic_publish.call_args.kwargs
        assert kw["routing_key"] == "evt.voucher.enviado"
        assert kw["exchange"] == "travelhub.events.exchange"

    @patch("modules.publishers.voucher_enviado_publisher.pika.BlockingConnection")
    def test_delivery_mode_persistent(self, mock_bc):
        from modules.publishers.voucher_enviado_publisher import publish_voucher_enviado
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_bc.return_value = mock_conn
        mock_conn.channel.return_value = mock_ch

        publish_voucher_enviado("res-003")

        props = mock_ch.basic_publish.call_args.kwargs["properties"]
        assert props.delivery_mode == 2


# ===========================================================================
# modules/consumers/reserva_confirmada_consumer.py – callback
# ===========================================================================

class TestConsumerCallback:
    """Tests for the RabbitMQ message callback."""

    def test_valid_event_with_data_key(self):
        from modules.consumers.reserva_confirmada_consumer import callback
        ch, method, props = _make_callback_mocks()
        body = json.dumps({
            "type": "ReservaConfirmadaEvt",
            "data": {"id_reserva": "r-1", "emailCliente": "a@b.com"},
        }).encode()

        with patch("modules.consumers.reserva_confirmada_consumer.send_voucher_email") as me, \
             patch("modules.consumers.reserva_confirmada_consumer.publish_voucher_enviado") as mp:
            callback(ch, method, props, body)

        me.assert_called_once_with("a@b.com", "r-1")
        mp.assert_called_once_with("r-1")
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)

    def test_valid_event_without_data_key_falls_back_to_root(self):
        """When 'data' key is absent, payload should be the root dict."""
        from modules.consumers.reserva_confirmada_consumer import callback
        ch, method, props = _make_callback_mocks()
        body = json.dumps({
            "type": "ReservaConfirmadaEvt",
            "id_reserva": "r-2",
            "emailCliente": "c@d.com",
        }).encode()

        with patch("modules.consumers.reserva_confirmada_consumer.send_voucher_email") as me, \
             patch("modules.consumers.reserva_confirmada_consumer.publish_voucher_enviado") as mp:
            callback(ch, method, props, body)

        me.assert_called_once_with("c@d.com", "r-2")
        mp.assert_called_once_with("r-2")

    def test_ignores_unknown_event_type(self):
        from modules.consumers.reserva_confirmada_consumer import callback
        ch, method, props = _make_callback_mocks()
        body = json.dumps({"type": "OtroEvento", "data": {}}).encode()

        with patch("modules.consumers.reserva_confirmada_consumer.send_voucher_email") as me, \
             patch("modules.consumers.reserva_confirmada_consumer.publish_voucher_enviado") as mp:
            callback(ch, method, props, body)

        me.assert_not_called()
        mp.assert_not_called()
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)

    def test_invalid_json_is_caught(self):
        from modules.consumers.reserva_confirmada_consumer import callback
        ch, method, props = _make_callback_mocks()
        # This should not propagate any exception
        callback(ch, method, props, b"not-valid-json")

    def test_exception_during_send_is_caught(self):
        from modules.consumers.reserva_confirmada_consumer import callback
        ch, method, props = _make_callback_mocks()
        body = json.dumps({
            "type": "ReservaConfirmadaEvt",
            "data": {"id_reserva": "r-3", "emailCliente": "e@f.com"},
        }).encode()

        with patch(
            "modules.consumers.reserva_confirmada_consumer.send_voucher_email",
            side_effect=RuntimeError("smtp error"),
        ):
            callback(ch, method, props, body)  # Must not raise

    def test_exception_prints_error(self, capsys):
        from modules.consumers.reserva_confirmada_consumer import callback
        ch, method, props = _make_callback_mocks()
        callback(ch, method, props, b"bad")
        out = capsys.readouterr().out
        assert "Error procesando evento" in out


# ===========================================================================
# modules/consumers/reserva_confirmada_consumer.py – _configure_consumer_channel
# ===========================================================================

class TestConfigureConsumerChannel:
    """Tests for channel setup helper."""

    def test_exchange_declared(self):
        from modules.consumers.reserva_confirmada_consumer import _configure_consumer_channel
        ch = MagicMock()
        _configure_consumer_channel(ch)
        ch.exchange_declare.assert_called_once_with(
            exchange="travelhub.events.exchange",
            exchange_type="topic",
            durable=True,
        )

    def test_queue_declared(self):
        from modules.consumers.reserva_confirmada_consumer import _configure_consumer_channel
        ch = MagicMock()
        _configure_consumer_channel(ch)
        ch.queue_declare.assert_called_once_with(
            queue="notification.events.queue",
            durable=True,
        )

    def test_queue_bound_to_exchange(self):
        from modules.consumers.reserva_confirmada_consumer import _configure_consumer_channel
        ch = MagicMock()
        _configure_consumer_channel(ch)
        ch.queue_bind.assert_called_once_with(
            exchange="travelhub.events.exchange",
            queue="notification.events.queue",
            routing_key="evt.reserva.confirmada",
        )

    def test_basic_consume_configured_correctly(self):
        from modules.consumers.reserva_confirmada_consumer import _configure_consumer_channel
        ch = MagicMock()
        _configure_consumer_channel(ch)
        kw = ch.basic_consume.call_args.kwargs
        assert kw.get("queue") == "notification.events.queue"
        assert kw.get("auto_ack") is False


# ===========================================================================
# modules/consumers/reserva_confirmada_consumer.py – start_consumer
# ===========================================================================

class TestStartConsumer:
    """Tests for the infinitely-looping start_consumer function."""

    @staticmethod
    def _raise_after(n, exc_type=KeyboardInterrupt):
        """Return a side-effect factory that raises exc_type after n calls."""
        counter = [0]
        def _side_effect(*args, **kwargs):
            counter[0] += 1
            if counter[0] > n:
                raise exc_type("stop test")
            raise pika.exceptions.AMQPConnectionError("no rabbit")
        return _side_effect

    @patch("modules.consumers.reserva_confirmada_consumer.time.sleep")
    @patch("modules.consumers.reserva_confirmada_consumer.create_connection")
    def test_reconnects_after_connection_error(self, mock_cc, mock_sleep):
        from modules.consumers.reserva_confirmada_consumer import start_consumer
        mock_cc.side_effect = self._raise_after(1)
        with pytest.raises(KeyboardInterrupt):
            start_consumer()
        assert mock_cc.call_count == 2
        mock_sleep.assert_called()

    @patch("modules.consumers.reserva_confirmada_consumer.time.sleep")
    @patch("modules.consumers.reserva_confirmada_consumer._configure_consumer_channel")
    @patch("modules.consumers.reserva_confirmada_consumer.create_connection")
    def test_closes_channel_and_connection_in_finally(self, mock_cc, mock_cfg, mock_sleep):
        from modules.consumers.reserva_confirmada_consumer import start_consumer
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
        mock_cfg.assert_called_once_with(mock_ch)

    @patch("modules.consumers.reserva_confirmada_consumer.time.sleep")
    @patch("modules.consumers.reserva_confirmada_consumer._configure_consumer_channel")
    @patch("modules.consumers.reserva_confirmada_consumer.create_connection")
    def test_prints_reconnect_when_consuming_stops_normally(self, mock_cc, mock_cfg, mock_sleep, capsys):
        from modules.consumers.reserva_confirmada_consumer import start_consumer
        mock_conn = MagicMock()
        mock_ch = MagicMock()
        mock_conn.channel.return_value = mock_ch
        mock_ch.start_consuming.return_value = None  # returns without raising

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
        assert "reconnecting" in out.lower() or "Consumer stopped" in out

    @patch("modules.consumers.reserva_confirmada_consumer.time.sleep")
    @patch("modules.consumers.reserva_confirmada_consumer.create_connection")
    def test_finally_skips_close_when_both_none(self, mock_cc, mock_sleep):
        """Channel and connection stay None when create_connection raises immediately."""
        from modules.consumers.reserva_confirmada_consumer import start_consumer
        mock_cc.side_effect = self._raise_after(1)
        with pytest.raises(KeyboardInterrupt):
            start_consumer()

    @patch("modules.consumers.reserva_confirmada_consumer.time.sleep")
    @patch("modules.consumers.reserva_confirmada_consumer._configure_consumer_channel")
    @patch("modules.consumers.reserva_confirmada_consumer.create_connection")
    def test_swallows_exceptions_raised_during_close(self, mock_cc, mock_cfg, mock_sleep):
        from modules.consumers.reserva_confirmada_consumer import start_consumer
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
            start_consumer()  # must not propagate the close exceptions


# ===========================================================================
# config/app.py
# ===========================================================================

class TestCreateApp:
    """Tests for the FastAPI application factory."""

    def test_returns_fastapi_instance(self):
        from fastapi import FastAPI
        with patch("config.app.start_consumer"):
            from config.app import create_app
            app = create_app()
        assert isinstance(app, FastAPI)

    def test_health_route_registered(self):
        with patch("config.app.start_consumer"):
            from config.app import create_app
            app = create_app()
        assert "/health" in [r.path for r in app.routes]

    def test_startup_creates_daemon_thread(self):
        # Patch `threading` in config.app's namespace (not globally) so
        # Starlette's own thread usage is unaffected.
        with patch("config.app.threading") as mock_threading, \
             patch("config.app.start_consumer"):
            mock_t = MagicMock()
            mock_threading.Thread.return_value = mock_t
            from config.app import create_app
            app = create_app()
            # Call startup handlers directly to avoid TestClient thread issues.
            for handler in app.router.on_startup:
                handler()
        mock_threading.Thread.assert_called_once()
        assert mock_threading.Thread.call_args.kwargs.get("daemon") is True
        mock_t.start.assert_called_once()

