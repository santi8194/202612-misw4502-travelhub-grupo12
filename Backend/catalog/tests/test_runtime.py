import json

import main as main_module
from catalog.modules.catalog.infrastructure.services import event_bus as event_bus_module


def test_start_rabbitmq_consumer_skips_when_events_are_disabled(monkeypatch, capsys):
	monkeypatch.setattr(main_module, "ENABLE_EVENTS", False)

	class FailingThread:
		def __init__(self, *args, **kwargs):
			raise AssertionError("thread should not be created when events are disabled")

	monkeypatch.setattr(main_module.threading, "Thread", FailingThread)

	main_module.start_rabbitmq_consumer()

	assert "ENABLE_EVENTS=false" in capsys.readouterr().out


def test_start_rabbitmq_consumer_starts_daemon_thread(monkeypatch):
	monkeypatch.setattr(main_module, "ENABLE_EVENTS", True)
	thread_state = {}

	class FakeThread:
		def __init__(self, target):
			thread_state["target"] = target
			thread_state["started"] = False
			self.daemon = False

		def start(self):
			thread_state["started"] = True
			thread_state["daemon"] = self.daemon

	monkeypatch.setattr(main_module.threading, "Thread", FakeThread)

	main_module.start_rabbitmq_consumer()

	assert thread_state["target"] is main_module.start_consumer
	assert thread_state["started"] is True
	assert thread_state["daemon"] is True


def test_event_bus_skips_publish_when_events_are_disabled(monkeypatch, capsys):
	monkeypatch.setattr(event_bus_module, "ENABLE_EVENTS", False)
	monkeypatch.setattr(
		event_bus_module,
		"create_connection",
		lambda: (_ for _ in ()).throw(AssertionError("connection should not be created")),
	)

	event_bus_module.EventBus().publish_event("catalog.test", "EventoTest", {"ok": True})

	assert "skipping publish" in capsys.readouterr().out


def test_event_bus_publishes_message_and_closes_connection(monkeypatch):
	monkeypatch.setattr(event_bus_module, "ENABLE_EVENTS", True)
	recorded = {}

	class FakeChannel:
		def exchange_declare(self, **kwargs):
			recorded.setdefault("exchange_calls", []).append(kwargs)

		def basic_publish(self, **kwargs):
			recorded["publish"] = kwargs

	class FakeConnection:
		is_open = True

		def __init__(self):
			self.channel_instance = FakeChannel()
			self.closed = False

		def channel(self):
			return self.channel_instance

		def close(self):
			self.closed = True
			recorded["closed"] = True

	connection = FakeConnection()
	monkeypatch.setattr(event_bus_module, "create_connection", lambda: connection)

	event_bus_module.EventBus().publish_event(
		"catalog.created",
		"CategoriaCreada",
		{"id_categoria": "123"},
	)

	assert len(recorded["exchange_calls"]) == 2
	assert recorded["publish"]["exchange"] == event_bus_module.EVENT_EXCHANGE
	assert recorded["publish"]["routing_key"] == "catalog.created"
	assert json.loads(recorded["publish"]["body"]) == {
		"type": "CategoriaCreada",
		"id_categoria": "123",
	}
	assert recorded["closed"] is True