from modules.payments.application.commands.process_payment import ProcessPayment


class _Repo:
    def __init__(self, existing=None):
        self._existing = existing
        self.saved = []

    def obtain_by_reservation(self, reservation_id):
        return self._existing

    def save(self, payment):
        self.saved.append(payment)


class _Bus:
    def __init__(self):
        self.events = []

    def publish_event(self, routing_key, event_type, payload):
        self.events.append((routing_key, event_type, payload))


def test_process_payment_returns_existing_payment_state():
    existing = type("ExistingPayment", (), {"state": "APROBADO"})
    repo = _Repo(existing=existing)
    bus = _Bus()
    command = ProcessPayment(repo, bus)

    result = command.execute("reserva-1", 120.0)

    assert result == {"message": "Payment already processed", "state": "APROBADO"}
    assert repo.saved == []
    assert bus.events == []


def test_process_payment_approves_when_amount_below_threshold(monkeypatch):
    monkeypatch.setattr("modules.payments.application.commands.process_payment.time.sleep", lambda _: None)
    repo = _Repo()
    bus = _Bus()
    command = ProcessPayment(repo, bus)

    result = command.execute("reserva-2", 4999.0)

    assert result["state"] == "APROBADO"
    assert result["event_generated"] == "PagoExitosoEvt"
    assert len(repo.saved) == 1
    assert bus.events[0][1] == "PagoExitosoEvt"


def test_process_payment_rejects_when_amount_is_high(monkeypatch):
    monkeypatch.setattr("modules.payments.application.commands.process_payment.time.sleep", lambda _: None)
    repo = _Repo()
    bus = _Bus()
    command = ProcessPayment(repo, bus)

    result = command.execute("reserva-3", 5000.0)

    assert result["state"] == "RECHAZADO"
    assert result["event_generated"] == "PagoRechazadoEvt"
    assert len(repo.saved) == 1
    assert bus.events[0][1] == "PagoRechazadoEvt"