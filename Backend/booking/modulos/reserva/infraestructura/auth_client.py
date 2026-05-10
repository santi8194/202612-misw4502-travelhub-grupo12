import json
import os
from urllib import request as urllib_request
from urllib.parse import quote


class AuthServiceClient:
    def __init__(self, base_url: str | None = None, timeout: int = 5):
        self.base_url = (base_url or os.getenv("AUTH_SERVICE_URL", "http://authservice:8000/auth")).rstrip("/")
        self.timeout = timeout

    def get_full_name(self, id_usuario: str) -> str | None:
        url = f"{self.base_url}/internal/users/{quote(id_usuario)}"
        req = urllib_request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("full_name")
        except Exception:
            return None
