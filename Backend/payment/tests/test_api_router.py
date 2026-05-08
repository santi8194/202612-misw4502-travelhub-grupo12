from fastapi.testclient import TestClient

from api import router as router_module
from config.app import create_app


def _client():
    return TestClient(create_app())


def test_health_endpoint():
    response = _client().get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "Payment Service running"}


def test_procesar_pago_delegates_to_command(monkeypatch):
    class FakeProcessPayment:
        def __init__(self, repository, event_bus):
            pass

        def execute(self, reservation_id, amount):
            return {
                "payment_id": "pay-123",
                "state": "APROBADO",
                "reservation_id": reservation_id,
                "amount": amount,
            }

    monkeypatch.setattr(router_module, "ProcessPayment", FakeProcessPayment)

    response = _client().post(
        "/procesar_pago",
        json={"id_reserva": "res-123", "monto": 250.0},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "APROBADO"
    assert body["reservation_id"] == "res-123"


def test_refund_payment_delegates_to_command(monkeypatch):
    class FakeRefundPayment:
        def __init__(self, repository, event_bus):
            pass

        def execute(self, payment_id):
            return {"reservation_id": payment_id, "state": "REFUNDED"}

    monkeypatch.setattr(router_module, "RefundPayment", FakeRefundPayment)

    response = _client().post(
        "/reversar_pago",
        json={"id_pago": "res-456"},
    )

    assert response.status_code == 200
    assert response.json() == {"reservation_id": "res-456", "state": "REFUNDED"}


def test_get_payments_by_reserva_delegates_to_query(monkeypatch):
    class FakeGetPaymentsByReservation:
        def __init__(self, repository):
            pass

        def execute(self, reservation_id):
            return [
                {
                    "id": "pay-123",
                    "reservation_id": reservation_id,
                    "amount": 100.0,
                    "currency": "USD",
                    "state": "APPROVED",
                }
            ]

    monkeypatch.setattr(router_module, "GetPaymentsByReservation", FakeGetPaymentsByReservation)

    response = _client().get("/payments/by-reserva/res-123")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["reservation_id"] == "res-123"
    assert body[0]["id"] == "pay-123"
