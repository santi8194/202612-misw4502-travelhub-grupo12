import json
import os
from urllib import request as urllib_request
from urllib.parse import quote


class PaymentServiceClient:
    def __init__(self, base_url: str | None = None, timeout: int = 5):
        self.base_url = (base_url or os.getenv("PAYMENT_SERVICE_URL", "http://payment:8002")).rstrip("/")
        self.timeout = timeout

    def get_payment_for_reserva(self, id_reserva: str) -> dict | None:
        url = f"{self.base_url}/payments/by-reserva/{quote(id_reserva)}"
        req = urllib_request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            return None
