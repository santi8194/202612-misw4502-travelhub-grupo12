from modules.payments.application.commands.refund_payment import RefundPayment


class _Repo:
    def __init__(self, payment=None):
        self.payment = payment
        self.saved = []

    def obtain_by_reservation(self, reservation_id):
        return self.payment

    def save(self, payment):
        self.saved.append(payment)


class _Bus:
    def __init__(self):
        self.events = []

    def publish_event(self, routing_key, event_type, payload):
        self.events.append((routing_key, event_type, payload))


def test_refund_payment_not_found():
    command = RefundPayment(_Repo(payment=None), _Bus())

    result = command.execute("reserva-x")

    assert result == {"error": "Payment not found"}


def test_refund_payment_already_refunded_returns_message_without_publishing():
    payment = type("Payment", (), {"id": "p-1", "reservation_id": "r-1", "state": "REFUNDED"})
    repo = _Repo(payment=payment)
    bus = _Bus()
    command = RefundPayment(repo, bus)

    result = command.execute("r-1")

    assert result == {"message": "Payment was already refunded", "state": "REFUNDED"}
    assert repo.saved == []
    assert bus.events == []


def test_refund_payment_marks_refunded_and_publishes_event():
    payment = type("Payment", (), {"id": "p-2", "reservation_id": "r-2", "state": "APROBADO"})
    repo = _Repo(payment=payment)
    bus = _Bus()
    command = RefundPayment(repo, bus)

    result = command.execute("r-2")

    assert result["state"] == "REFUNDED"
    assert result["event_generated"] == "PagoReversadoEvt"
    assert len(repo.saved) == 1
    assert bus.events[0][1] == "PagoReversadoEvt"