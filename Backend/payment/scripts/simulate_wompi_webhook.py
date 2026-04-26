import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
import uuid


def main() -> None:
    parser = argparse.ArgumentParser(description="Simula un webhook de Wompi para payments.")
    parser.add_argument("--reference", required=True, help="Referencia PAY-* devuelta por POST /payments")
    parser.add_argument("--status", default="APPROVED", choices=["APPROVED", "DECLINED", "ERROR", "VOIDED"])
    parser.add_argument("--amount-in-cents", required=True, type=int)
    parser.add_argument("--url", default="http://127.0.0.1:8000/webhook")
    args = parser.parse_args()

    payload = build_payload(args.reference, args.status, args.amount_in_cents)
    response_status, response_body = post_json(args.url, payload)

    print(f"HTTP {response_status}")
    print(response_body)


def build_payload(reference: str, status: str, amount_in_cents: int) -> dict:
    transaction_id = f"wompi-test-{uuid.uuid4()}"
    timestamp = int(time.time())
    secret = os.getenv("WOMPI_EVENTS_SECRET", "test_events_secret")
    raw_checksum = f"{transaction_id}{status}{amount_in_cents}{timestamp}{secret}"
    checksum = hashlib.sha256(raw_checksum.encode("utf-8")).hexdigest()

    return {
        "event": "transaction.updated",
        "timestamp": timestamp,
        "data": {
            "transaction": {
                "id": transaction_id,
                "reference": reference,
                "status": status,
                "amount_in_cents": amount_in_cents,
            }
        },
        "signature": {
            "properties": [
                "transaction.id",
                "transaction.status",
                "transaction.amount_in_cents",
            ],
            "checksum": checksum,
        },
    }


def post_json(url: str, payload: dict) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url=url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8")


if __name__ == "__main__":
    main()

