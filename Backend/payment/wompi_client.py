import hashlib
import os
from typing import Any

import httpx


class WompiAPIError(Exception):
    def __init__(self, message: str, status_code: int = 502, payload: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


def build_checkout_data(reference: str, amount_in_cents: int, currency: str) -> dict[str, Any]:
    public_key = os.getenv("WOMPI_PUBLIC_KEY", "pub_test_local")

    return {
        "public_key": public_key,
        "currency": currency,
        "amount_in_cents": amount_in_cents,
        "reference": reference,
        "signature_integrity": build_integrity_signature(reference, amount_in_cents, currency),
    }


def verify_event(payload: dict[str, Any], header_checksum: str | None = None) -> bool:
    signature = payload.get("signature") or {}
    properties = signature.get("properties") or []
    checksum = header_checksum or signature.get("checksum")
    timestamp = payload.get("timestamp")
    events_secret = os.getenv("WOMPI_EVENTS_SECRET", "test_events_secret")

    if not properties or not checksum or timestamp is None:
        return False

    values = "".join(value_as_text(get_nested_value(payload, prop)) for prop in properties)
    expected_checksum = sha256(f"{values}{timestamp}{events_secret}")
    return expected_checksum == checksum


def map_wompi_status(status: str | None) -> str:
    normalized_status = (status or "").upper()
    if normalized_status == "APPROVED":
        return "APPROVED"
    if normalized_status in {"DECLINED", "ERROR", "VOIDED"}:
        return "REJECTED"
    return "PENDING"


def get_nested_value(payload: dict[str, Any], path: str) -> Any:
    value = find_nested_value(payload.get("data", {}), path)
    if value is not None:
        return value
    return find_nested_value(payload, path)


def find_nested_value(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def value_as_text(value: Any) -> str:
    return "" if value is None else str(value)


def get_public_key() -> str:
    return get_required_setting("WOMPI_PUBLIC_KEY")


def get_private_key() -> str:
    return get_required_setting("WOMPI_PRIVATE_KEY")


def get_required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Falta configurar la variable de entorno {name}")
    return value


def get_base_url() -> str:
    configured = os.getenv("WOMPI_BASE_URL")
    if configured:
        return configured.rstrip("/")

    public_key = os.getenv("WOMPI_PUBLIC_KEY", "")
    private_key = os.getenv("WOMPI_PRIVATE_KEY", "")
    if public_key.startswith("pub_prod_") or private_key.startswith("priv_prod_"):
        return "https://production.wompi.co/v1"
    return "https://sandbox.wompi.co/v1"


def get_payouts_base_url() -> str:
    configured = os.getenv("WOMPI_PAYOUTS_BASE_URL")
    if configured:
        return configured.rstrip("/")

    private_key = os.getenv("WOMPI_PRIVATE_KEY", "")
    if private_key.startswith("priv_prod_"):
        return "https://api.payouts.wompi.co/v1"
    return "https://api.sandbox.payouts.wompi.co/v1"


def build_integrity_signature(
    reference: str,
    amount_in_cents: int,
    currency: str,
    expiration_time: str | None = None,
) -> str:
    integrity_secret = os.getenv("WOMPI_INTEGRITY_SECRET", "test_integrity_secret")
    raw_signature = f"{reference}{amount_in_cents}{currency}"
    if expiration_time:
        raw_signature += expiration_time
    raw_signature += integrity_secret
    return sha256(raw_signature)


def fetch_acceptance_tokens() -> dict[str, Any]:
    public_key = get_public_key()
    payload = wompi_request("GET", f"/merchants/{public_key}", auth_key=public_key)
    merchant_data = payload.get("data", {})
    return {
        "acceptance": merchant_data.get("presigned_acceptance", {}),
        "personal_data_auth": merchant_data.get("presigned_personal_data_auth", {}),
    }


def tokenize_card(card_data: dict[str, Any]) -> dict[str, Any]:
    public_key = get_public_key()
    payload = wompi_request("POST", "/tokens/cards", auth_key=public_key, json_body=card_data)
    token_data = payload.get("data", {})
    return {
        "data": {
            "id": token_data.get("id"),
            "status": payload.get("status", ""),
            "created_at": token_data.get("created_at"),
            "brand": token_data.get("brand"),
            "name": token_data.get("name"),
            "last_four": token_data.get("last_four"),
            "bin": token_data.get("bin"),
            "exp_year": token_data.get("exp_year"),
            "exp_month": token_data.get("exp_month"),
            "card_holder": token_data.get("card_holder"),
            "expires_at": token_data.get("expires_at"),
        }
    }


def create_payment_source(
    *,
    card_token: str,
    customer_email: str,
    acceptance_token: str,
    accept_personal_auth: str,
) -> dict[str, Any]:
    private_key = get_private_key()
    return wompi_request(
        "POST",
        "/payment_sources",
        auth_key=private_key,
        json_body={
            "type": "CARD",
            "token": card_token,
            "customer_email": customer_email,
            "acceptance_token": acceptance_token,
            "accept_personal_auth": accept_personal_auth,
        },
    )


def create_card_transaction(
    *,
    amount_in_cents: int,
    currency: str,
    customer_email: str,
    acceptance_token: str,
    accept_personal_auth: str,
    reference: str,
    payment_source_id: int,
    installments: int,
    redirect_url: str | None = None,
    ip_address: str | None = None,
    recurrent: bool | None = None,
) -> dict[str, Any]:
    private_key = get_private_key()
    payload: dict[str, Any] = {
        "amount_in_cents": amount_in_cents,
        "currency": currency,
        "customer_email": customer_email,
        "payment_method": {
            "installments": installments,
        },
        "reference": reference,
        "payment_source_id": payment_source_id,
        "acceptance_token": acceptance_token,
        "accept_personal_auth": accept_personal_auth,
        "signature": build_integrity_signature(reference, amount_in_cents, currency),
    }
    if redirect_url:
        payload["redirect_url"] = redirect_url
    if ip_address:
        payload["ip"] = ip_address
    if recurrent is not None:
        payload["recurrent"] = recurrent

    return wompi_request("POST", "/transactions", auth_key=private_key, json_body=payload)


def fetch_transaction(transaction_id: str) -> dict[str, Any]:
    public_key = get_public_key()
    return wompi_request("GET", f"/transactions/{transaction_id}", auth_key=public_key)


def wompi_request(
    method: str,
    path: str,
    *,
    auth_key: str,
    json_body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = f"{get_base_url()}{path}"
    headers = {
        "Authorization": f"Bearer {auth_key}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.request(method, url, headers=headers, json=json_body, timeout=15.0)
    except httpx.HTTPError as exc:
        raise WompiAPIError("No se pudo conectar con Wompi", status_code=502) from exc

    payload = parse_json_response(response)
    if response.status_code >= 400:
        raise WompiAPIError(extract_error_message(payload), status_code=response.status_code, payload=payload)

    return payload


def parse_json_response(response: httpx.Response) -> dict[str, Any]:
    try:
        body = response.json()
    except ValueError:
        body = {}
    return body if isinstance(body, dict) else {}


def extract_error_message(payload: dict[str, Any]) -> str:
    error = payload.get("error")
    if isinstance(error, dict):
        return error.get("reason") or error.get("messages") or error.get("type") or "Error de Wompi"
    if isinstance(error, str):
        return error
    return "Error de Wompi"


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
