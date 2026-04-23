import hashlib

from fastapi.testclient import TestClient

import app as payment_app


client = TestClient(payment_app.app)


def setup_function():
    payment_app.payments_by_id.clear()
    payment_app.payment_id_by_reference.clear()


def test_healthcheck_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "payment"}


def test_create_payment_returns_widget_checkout_data(monkeypatch):
    monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_123")
    monkeypatch.setenv("WOMPI_INTEGRITY_SECRET", "integrity_secret")

    response = client.post(
        "/payments",
        json={"id_reserva": "reserva-1", "monto": 12000, "moneda": "COP"},
    )

    body = response.json()
    checkout = body["checkout"]

    assert response.status_code == 201
    assert body["estado"] == "PENDING"
    assert body["id_reserva"] == "reserva-1"
    assert checkout["public_key"] == "pub_test_123"
    assert checkout["reference"] == body["referencia"]
    assert checkout["amount_in_cents"] == 1200000
    assert checkout["signature_integrity"]


def test_create_payment_requires_id_reserva():
    response = client.post("/payments", json={"monto": 1000, "moneda": "COP"})

    assert response.status_code == 422


def test_create_payment_rejects_invalid_amount():
    response = client.post(
        "/payments",
        json={"id_reserva": "reserva-1", "monto": 0, "moneda": "COP"},
    )

    assert response.status_code == 422


def test_get_payment_returns_existing_payment():
    create_response = client.post(
        "/payments",
        json={"id_reserva": "reserva-1", "monto": 1000, "moneda": "COP"},
    )
    id_pago = create_response.json()["id_pago"]

    response = client.get(f"/payments/{id_pago}")

    assert response.status_code == 200
    assert response.json()["id_pago"] == id_pago


def test_list_payments_returns_all_created_payments():
    client.post("/payments", json={"id_reserva": "reserva-1", "monto": 1000, "moneda": "COP"})
    client.post("/payments", json={"id_reserva": "reserva-2", "monto": 2000, "moneda": "COP"})

    response = client.get("/payments")
    body = response.json()

    assert response.status_code == 200
    assert len(body) == 2
    assert {payment["id_reserva"] for payment in body} == {"reserva-1", "reserva-2"}


def test_get_payment_returns_404_when_missing():
    response = client.get("/payments/no-existe")

    assert response.status_code == 404


def test_webhook_approved_updates_payment_and_publishes_event(monkeypatch):
    monkeypatch.setenv("WOMPI_EVENTS_SECRET", "events_secret")
    published_events = []
    monkeypatch.setattr(
        payment_app,
        "publish_payment_event",
        lambda payment, event_type, routing_key: published_events.append((event_type, routing_key)) or True,
    )
    payment = create_pending_payment()
    payload = build_wompi_payload(payment["referencia"], "APPROVED", "trx-1")

    response = client.post("/webhook", json=payload)

    assert response.status_code == 200
    assert response.json()["estado"] == "APPROVED"
    assert payment_app.payments_by_id[payment["id_pago"]]["estado"] == "APPROVED"
    assert published_events == [("PagoExitosoEvt", "evt.pago.exitoso")]


def test_webhook_declined_updates_payment_as_rejected(monkeypatch):
    monkeypatch.setenv("WOMPI_EVENTS_SECRET", "events_secret")
    published_events = []
    monkeypatch.setattr(
        payment_app,
        "publish_payment_event",
        lambda payment, event_type, routing_key: published_events.append((event_type, routing_key)) or True,
    )
    payment = create_pending_payment()
    payload = build_wompi_payload(payment["referencia"], "DECLINED", "trx-2")

    response = client.post("/webhook", json=payload)

    assert response.status_code == 200
    assert response.json()["estado"] == "REJECTED"
    assert published_events == [("PagoRechazadoEvt", "evt.pago.rechazado")]


def test_webhook_rejects_invalid_signature(monkeypatch):
    monkeypatch.setenv("WOMPI_EVENTS_SECRET", "events_secret")
    payment = create_pending_payment()
    payload = build_wompi_payload(payment["referencia"], "APPROVED", "trx-3")
    payload["signature"]["checksum"] = "bad-signature"

    response = client.post("/webhook", json=payload)

    assert response.status_code == 401


def test_duplicate_webhook_does_not_publish_twice(monkeypatch):
    monkeypatch.setenv("WOMPI_EVENTS_SECRET", "events_secret")
    published_events = []
    monkeypatch.setattr(
        payment_app,
        "publish_payment_event",
        lambda payment, event_type, routing_key: published_events.append((event_type, routing_key)) or True,
    )
    payment = create_pending_payment()
    payload = build_wompi_payload(payment["referencia"], "APPROVED", "trx-4")

    first_response = client.post("/webhook", json=payload)
    second_response = client.post("/webhook", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert published_events == [("PagoExitosoEvt", "evt.pago.exitoso")]


def create_pending_payment():
    response = client.post(
        "/payments",
        json={"id_reserva": "reserva-1", "monto": 1000, "moneda": "COP"},
    )
    return response.json()


def build_wompi_payload(reference: str, status: str, transaction_id: str):
    payload = {
        "event": "transaction.updated",
        "timestamp": 1713900000,
        "data": {
            "transaction": {
                "id": transaction_id,
                "reference": reference,
                "status": status,
                "amount_in_cents": 100000,
            }
        },
        "signature": {
            "properties": [
                "transaction.id",
                "transaction.status",
                "transaction.amount_in_cents",
            ],
            "checksum": "",
        },
    }
    raw = f"{transaction_id}{status}100000{payload['timestamp']}events_secret"
    payload["signature"]["checksum"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return payload
