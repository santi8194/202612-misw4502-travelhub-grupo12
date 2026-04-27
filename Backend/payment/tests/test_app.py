import hashlib

from fastapi.testclient import TestClient

import app as payment_app


client = TestClient(payment_app.app)


def setup_function():
    payment_app.payments_by_id.clear()
    payment_app.payment_id_by_reference.clear()


def test_get_acceptance_tokens_returns_presigned_documents(monkeypatch):
    monkeypatch.setattr(
        payment_app,
        "fetch_acceptance_tokens",
        lambda: {
            "acceptance": {
                "acceptance_token": "accept-token",
                "permalink": "https://wompi.co/privacy.pdf",
                "type": "END_USER_POLICY",
            },
            "personal_data_auth": {
                "acceptance_token": "personal-token",
                "permalink": "https://wompi.co/personal-data.pdf",
                "type": "PERSONAL_DATA_AUTH",
            },
        },
    )

    response = client.get("/payments/acceptance-tokens")

    assert response.status_code == 200
    assert response.json()["acceptance"]["acceptance_token"] == "accept-token"
    assert response.json()["personal_data_auth"]["acceptance_token"] == "personal-token"


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


def test_tokenize_card_returns_tokenized_card_data(monkeypatch):
    monkeypatch.setattr(
        payment_app,
        "tokenize_card",
        lambda _payload: {
            "data": {
                "id": "tok_test_123",
                "status": "CREATED",
                "brand": "VISA",
                "last_four": "4242",
                "card_holder": "Pedro Perez",
            }
        },
    )

    response = client.post(
        "/payments/cards/tokenize",
        json={
            "number": "4242424242424242",
            "exp_month": "06",
            "exp_year": "29",
            "cvc": "123",
            "card_holder": "Pedro Perez",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["id"] == "tok_test_123"
    assert response.json()["data"]["status"] == "CREATED"


def test_create_card_payment_creates_payment_source_and_transaction(monkeypatch):
    monkeypatch.setattr(
        payment_app,
        "create_payment_source",
        lambda **_kwargs: {"data": {"id": 3891, "status": "AVAILABLE"}},
    )
    monkeypatch.setattr(
        payment_app,
        "create_card_transaction",
        lambda **_kwargs: {
            "data": {
                "id": "trx-card-1",
                "status": "PENDING",
                "status_message": "La transacción está siendo procesada",
                "payment_method_type": "CARD",
                "payment_method": {
                    "brand": "VISA",
                    "last_four": "4242",
                },
            }
        },
    )

    response = client.post(
        "/payments/cards",
        json={
            "id_reserva": "reserva-card-1",
            "monto": 150000,
            "moneda": "COP",
            "customer_email": "cliente@travelhub.com",
            "acceptance_token": "accept-token",
            "accept_personal_auth": "personal-token",
            "card_token": "tok_test_123",
            "installments": 2,
        },
    )

    body = response.json()

    assert response.status_code == 201
    assert body["estado"] == "PENDING"
    assert body["wompi_transaction_id"] == "trx-card-1"
    assert body["payment_source_id"] == 3891
    assert body["payment_method_type"] == "CARD"
    assert body["card_last_four"] == "4242"
    assert body["checkout"] is None


def test_create_card_payment_can_use_existing_payment_source(monkeypatch):
    create_payment_source_called = False

    def unexpected_source_creation(**_kwargs):
        nonlocal create_payment_source_called
        create_payment_source_called = True
        return {"data": {"id": 3891}}

    monkeypatch.setattr(payment_app, "create_payment_source", unexpected_source_creation)
    monkeypatch.setattr(
        payment_app,
        "create_card_transaction",
        lambda **_kwargs: {
            "data": {
                "id": "trx-card-2",
                "status": "APPROVED",
                "status_message": "Transacción aprobada",
                "payment_method_type": "CARD",
                "payment_method": {
                    "brand": "MASTERCARD",
                    "last_four": "1111",
                },
            }
        },
    )
    monkeypatch.setattr(payment_app, "publish_payment_event", lambda *_args, **_kwargs: True)

    response = client.post(
        "/payments/cards",
        json={
            "id_reserva": "reserva-card-2",
            "monto": 80000,
            "moneda": "COP",
            "customer_email": "cliente@travelhub.com",
            "acceptance_token": "accept-token",
            "accept_personal_auth": "personal-token",
            "payment_source_id": 777,
            "installments": 1,
        },
    )

    assert response.status_code == 201
    assert response.json()["estado"] == "APPROVED"
    assert response.json()["payment_source_id"] == 777
    assert create_payment_source_called is False


def test_create_card_payment_requires_token_or_payment_source():
    response = client.post(
        "/payments/cards",
        json={
            "id_reserva": "reserva-card-3",
            "monto": 80000,
            "moneda": "COP",
            "customer_email": "cliente@travelhub.com",
            "acceptance_token": "accept-token",
            "accept_personal_auth": "personal-token",
            "installments": 1,
        },
    )

    assert response.status_code == 422


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


def test_get_payment_by_reserva_returns_existing_payment():
    client.post(
        "/payments",
        json={"id_reserva": "reserva-1", "monto": 1000, "moneda": "COP"},
    )

    response = client.get("/payments/by-reserva/reserva-1")

    assert response.status_code == 200
    assert response.json()["id_reserva"] == "reserva-1"


def test_get_payment_by_reserva_returns_404_when_missing():
    response = client.get("/payments/by-reserva/no-existe")

    assert response.status_code == 404


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


def test_get_transaction_status_proxies_wompi(monkeypatch):
    monkeypatch.setattr(
        payment_app,
        "fetch_transaction",
        lambda transaction_id: {"data": {"id": transaction_id, "status": "APPROVED"}},
    )

    response = client.get("/payments/transactions/trx-123")

    assert response.status_code == 200
    assert response.json()["data"]["id"] == "trx-123"
    assert response.json()["data"]["status"] == "APPROVED"


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


def test_create_payment_auto_approves_and_publishes_event_when_flag_enabled(monkeypatch):
    monkeypatch.setenv("PAYMENT_AUTO_APPROVE", "true")
    monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_123")
    monkeypatch.setenv("WOMPI_INTEGRITY_SECRET", "integrity_secret")
    published_events = []
    monkeypatch.setattr(
        payment_app,
        "publish_payment_event",
        lambda payment, event_type, routing_key: published_events.append((event_type, routing_key)) or True,
    )

    response = client.post(
        "/payments",
        json={"id_reserva": "reserva-auto", "monto": 5000, "moneda": "COP"},
    )

    body = response.json()
    assert response.status_code == 201
    assert body["estado"] == "APPROVED"
    assert published_events == [("PagoExitosoEvt", "evt.pago.exitoso")]


def test_create_payment_does_not_auto_approve_when_flag_disabled(monkeypatch):
    monkeypatch.setenv("PAYMENT_AUTO_APPROVE", "false")
    monkeypatch.setenv("WOMPI_PUBLIC_KEY", "pub_test_123")
    monkeypatch.setenv("WOMPI_INTEGRITY_SECRET", "integrity_secret")
    published_events = []
    monkeypatch.setattr(
        payment_app,
        "publish_payment_event",
        lambda payment, event_type, routing_key: published_events.append((event_type, routing_key)) or True,
    )

    response = client.post(
        "/payments",
        json={"id_reserva": "reserva-no-auto", "monto": 5000, "moneda": "COP"},
    )

    body = response.json()
    assert response.status_code == 201
    assert body["estado"] == "PENDING"
    assert published_events == []


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
