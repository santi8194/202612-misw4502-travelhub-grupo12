from modules.payments.infrastructure.services import handlers as handlers_module


def test_handle_process_payment_builds_use_case_and_executes(monkeypatch):
    captured = {}
    monkeypatch.setenv("PAYMENT_MODE", "mock")

    class FakeProcessPayment:
        def __init__(self, repository, event_bus):
            captured["repository"] = repository
            captured["event_bus"] = event_bus

        def execute(self, reservation_id, amount):
            captured["execute"] = (reservation_id, amount)
            return {"ok": True}

    monkeypatch.setattr(handlers_module, "PaymentRepository", lambda: "repo")
    monkeypatch.setattr(handlers_module, "EventBus", lambda: "bus")
    monkeypatch.setattr(handlers_module, "ProcessPayment", FakeProcessPayment)

    handlers_module.handle_process_payment({"id_reserva": "res-100", "monto": 999.0})

    assert captured["repository"] == "repo"
    assert captured["event_bus"] == "bus"
    assert captured["execute"] == ("res-100", 999.0)


def test_handle_refund_payment_builds_use_case_and_executes(monkeypatch):
    captured = {}
    monkeypatch.setenv("PAYMENT_MODE", "mock")

    class FakeRefundPayment:
        def __init__(self, repository, event_bus):
            captured["repository"] = repository
            captured["event_bus"] = event_bus

        def execute(self, reservation_id):
            captured["execute"] = reservation_id
            return {"ok": True}

    monkeypatch.setattr(handlers_module, "PaymentRepository", lambda: "repo")
    monkeypatch.setattr(handlers_module, "EventBus", lambda: "bus")
    monkeypatch.setattr(handlers_module, "RefundPayment", FakeRefundPayment)

    handlers_module.handle_refund_payment({"id_reserva": "res-200"})

    assert captured["repository"] == "repo"
    assert captured["event_bus"] == "bus"
    assert captured["execute"] == "res-200"


def test_handle_process_payment_wompi_mode_waits_for_webhook(monkeypatch):
    monkeypatch.setenv("PAYMENT_MODE", "wompi")
    monkeypatch.delenv("PAYMENT_AUTO_APPROVE", raising=False)

    result = handlers_module.handle_process_payment({"id_reserva": "res-300", "monto": 999.0})

    assert result == {"message": "Waiting for Wompi webhook", "state": "PENDING"}


def test_handle_process_payment_auto_approve_enabled_publishes_success_event(monkeypatch):
    monkeypatch.setenv("PAYMENT_MODE", "wompi")
    monkeypatch.setenv("PAYMENT_AUTO_APPROVE", "true")

    published = {}

    class FakeEventBus:
        def publish_event(self, routing_key, event_type, payload):
            published["routing_key"] = routing_key
            published["event_type"] = event_type
            published["payload"] = payload

    monkeypatch.setattr(handlers_module, "EventBus", FakeEventBus)

    result = handlers_module.handle_process_payment({"id_reserva": "res-301", "monto": 500.0})

    assert result["state"] == "APPROVED"
    assert result["reservation_id"] == "res-301"
    assert published["routing_key"] == "evt.pago.exitoso"
    assert published["event_type"] == "PagoExitosoEvt"
    assert published["payload"]["id_reserva"] == "res-301"
