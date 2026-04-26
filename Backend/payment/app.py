import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

import pika
from fastapi import FastAPI, Header, HTTPException, Request

from models import (
    AcceptanceTokensResponse,
    CardTokenizationRequest,
    CardTokenizationResponse,
    CreateCardPaymentRequest,
    CreatePaymentRequest,
    PaymentResponse,
)
from wompi_client import (
    WompiAPIError,
    build_checkout_data,
    create_card_transaction,
    create_payment_source,
    fetch_acceptance_tokens,
    fetch_transaction,
    map_wompi_status,
    tokenize_card,
    verify_event,
)

SERVICE_NAME = "payment"
FINAL_STATES = {"APPROVED", "REJECTED", "CANCELLED"}
EVENTS_EXCHANGE = "travelhub.events.exchange"

app = FastAPI(title="TravelHub Payment Service")
logger = logging.getLogger(SERVICE_NAME)
logging.basicConfig(level=logging.INFO)

payments_by_id: dict[str, dict[str, Any]] = {}
payment_id_by_reference: dict[str, str] = {}


def healthcheck() -> str:
    return "ok"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": healthcheck(), "service": SERVICE_NAME}


@app.get("/payments/acceptance-tokens", response_model=AcceptanceTokensResponse)
def get_acceptance_tokens() -> dict[str, Any]:
    return handle_wompi_call(fetch_acceptance_tokens)


@app.post("/payments", response_model=PaymentResponse, status_code=201)
def create_payment(request: CreatePaymentRequest) -> dict[str, Any]:
    id_pago = str(uuid.uuid4())
    reference = f"PAY-{id_pago}"
    amount_in_cents = int(round(request.monto * 100))
    currency = request.moneda.upper()

    checkout = build_checkout_data(reference, amount_in_cents, currency)
    now = utc_now()
    payment = {
        "id_pago": id_pago,
        "id_reserva": request.id_reserva,
        "referencia": reference,
        "estado": "PENDING",
        "monto": request.monto,
        "moneda": currency,
        "wompi_transaction_id": None,
        "payment_source_id": None,
        "payment_method_type": "CHECKOUT",
        "customer_email": None,
        "status_message": "Pendiente de confirmación por checkout",
        "card_brand": None,
        "card_last_four": None,
        "checkout": checkout,
        "created_at": now,
        "updated_at": now,
        "event_published": False,
    }

    payments_by_id[id_pago] = payment
    payment_id_by_reference[reference] = id_pago
    return payment


@app.post("/payments/cards/tokenize", response_model=CardTokenizationResponse)
def tokenize_card_payment_method(request: CardTokenizationRequest) -> dict[str, Any]:
    return handle_wompi_call(tokenize_card, request.model_dump())


@app.post("/payments/cards", response_model=PaymentResponse, status_code=201)
def create_card_payment(request: CreateCardPaymentRequest, http_request: Request) -> dict[str, Any]:
    id_pago = str(uuid.uuid4())
    reference = f"PAY-{id_pago}"
    amount_in_cents = int(round(request.monto * 100))
    currency = request.moneda.upper()

    payment_source_id = request.payment_source_id
    if payment_source_id is None:
        source_payload = handle_wompi_call(
            create_payment_source,
            card_token=request.card_token or "",
            customer_email=request.customer_email,
            acceptance_token=request.acceptance_token,
            accept_personal_auth=request.accept_personal_auth,
        )
        payment_source_id = source_payload.get("data", {}).get("id")
        if payment_source_id is None:
            raise HTTPException(status_code=502, detail="Wompi no retornó un payment_source_id válido")

    transaction_payload = handle_wompi_call(
        create_card_transaction,
        amount_in_cents=amount_in_cents,
        currency=currency,
        customer_email=request.customer_email,
        acceptance_token=request.acceptance_token,
        accept_personal_auth=request.accept_personal_auth,
        reference=reference,
        payment_source_id=payment_source_id,
        installments=request.installments,
        redirect_url=request.redirect_url,
        ip_address=extract_client_ip(http_request),
        recurrent=request.recurrent,
    )

    transaction = transaction_payload.get("data", {})
    transaction_state = map_wompi_status(transaction.get("status"))
    now = utc_now()
    payment = {
        "id_pago": id_pago,
        "id_reserva": request.id_reserva,
        "referencia": reference,
        "estado": transaction_state,
        "monto": request.monto,
        "moneda": currency,
        "wompi_transaction_id": transaction.get("id"),
        "payment_source_id": payment_source_id,
        "payment_method_type": transaction.get("payment_method_type", "CARD"),
        "customer_email": request.customer_email,
        "status_message": transaction.get("status_message"),
        "card_brand": transaction.get("payment_method", {}).get("brand"),
        "card_last_four": transaction.get("payment_method", {}).get("last_four"),
        "checkout": None,
        "created_at": now,
        "updated_at": now,
        "event_published": False,
    }

    payments_by_id[id_pago] = payment
    payment_id_by_reference[reference] = id_pago

    if transaction_state in {"APPROVED", "REJECTED"}:
        maybe_publish_final_event(payment)

    return payment


@app.get("/payments", response_model=list[PaymentResponse])
def list_payments() -> list[dict[str, Any]]:
    return list(payments_by_id.values())


@app.get("/payments/by-reserva/{id_reserva}", response_model=PaymentResponse)
def get_payment_by_reserva(id_reserva: str) -> dict[str, Any]:
    for payment in payments_by_id.values():
        if payment["id_reserva"] == id_reserva:
            return payment
    raise HTTPException(status_code=404, detail="Pago no encontrado para la reserva")


@app.get("/payments/{id_pago}", response_model=PaymentResponse)
def get_payment(id_pago: str) -> dict[str, Any]:
    payment = payments_by_id.get(id_pago)
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return payment


@app.get("/payments/transactions/{transaction_id}")
def get_transaction_status(transaction_id: str) -> dict[str, Any]:
    return handle_wompi_call(fetch_transaction, transaction_id)


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_event_checksum: str | None = Header(default=None),
) -> dict[str, Any]:
    payload = await request.json()

    if not verify_event(payload, x_event_checksum):
        raise HTTPException(status_code=401, detail="Firma de webhook invalida")

    event_name = payload.get("event")
    transaction = payload.get("data", {}).get("transaction", {})
    reference = transaction.get("reference")
    wompi_status = transaction.get("status")

    if event_name != "transaction.updated":
        return {"message": "Evento ignorado", "event": event_name}

    if not reference:
        raise HTTPException(status_code=400, detail="Webhook sin referencia de pago")

    payment_id = payment_id_by_reference.get(reference)
    if not payment_id:
        raise HTTPException(status_code=404, detail="Pago no encontrado para la referencia")

    payment = payments_by_id[payment_id]
    new_status = map_wompi_status(wompi_status)
    old_status = payment["estado"]

    if old_status in FINAL_STATES:
        maybe_publish_final_event(payment)
        return {"message": "Pago ya estaba finalizado", "estado": old_status}

    payment["estado"] = new_status
    payment["wompi_transaction_id"] = transaction.get("id")
    payment["payment_method_type"] = transaction.get("payment_method_type", payment.get("payment_method_type"))
    payment["status_message"] = transaction.get("status_message", payment.get("status_message"))
    payment["updated_at"] = utc_now()

    if new_status in {"APPROVED", "REJECTED"}:
        maybe_publish_final_event(payment)

    return {
        "message": "Webhook procesado",
        "id_pago": payment["id_pago"],
        "estado": payment["estado"],
    }


def maybe_publish_final_event(payment: dict[str, Any]) -> None:
    if payment.get("event_published"):
        return

    if payment["estado"] == "APPROVED":
        payment["event_published"] = publish_payment_event(payment, "PagoExitosoEvt", "evt.pago.exitoso")
    elif payment["estado"] == "REJECTED":
        payment["event_published"] = publish_payment_event(payment, "PagoRechazadoEvt", "evt.pago.rechazado")


def publish_payment_event(payment: dict[str, Any], event_type: str, routing_key: str) -> bool:
    body = {
        "type": event_type,
        "data": {
            "id_reserva": payment["id_reserva"],
            "id_pago": payment["id_pago"],
            "referencia": payment["referencia"],
            "wompi_transaction_id": payment.get("wompi_transaction_id"),
            "estado": payment["estado"],
        },
    }

    try:
        host = os.getenv("RABBITMQ_HOST", "localhost")
        port = int(os.getenv("RABBITMQ_PORT", "5672"))
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
        channel = connection.channel()
        channel.exchange_declare(exchange=EVENTS_EXCHANGE, exchange_type="topic", durable=True)
        channel.basic_publish(
            exchange=EVENTS_EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(body),
            properties=pika.BasicProperties(content_type="application/json", type=event_type),
        )
        connection.close()
        logger.info("Evento de pago publicado: %s", event_type)
        return True
    except Exception as exc:
        logger.warning("No se pudo publicar evento de pago en RabbitMQ: %s", exc)
        return False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


def handle_wompi_call(func: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
    try:
        return func(*args, **kwargs)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except WompiAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
