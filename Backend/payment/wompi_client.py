import hashlib
import os
from typing import Any


def build_checkout_data(reference: str, amount_in_cents: int, currency: str) -> dict[str, Any]:
    integrity_secret = os.getenv("WOMPI_INTEGRITY_SECRET", "test_integrity_secret")
    public_key = os.getenv("WOMPI_PUBLIC_KEY", "pub_test_local")
    raw_signature = f"{reference}{amount_in_cents}{currency}{integrity_secret}"

    return {
        "public_key": public_key,
        "currency": currency,
        "amount_in_cents": amount_in_cents,
        "reference": reference,
        "signature_integrity": sha256(raw_signature),
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


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
