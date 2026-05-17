import json
import os
from urllib import error as urllib_error
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

    def get_current_user(self, authorization_header: str | None) -> dict | None:
        if not authorization_header or not authorization_header.strip():
            return None

        url = f"{self.base_url}/me"
        req = urllib_request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": authorization_header,
            },
        )
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:
            if exc.code in (401, 403):
                return None
            raise RuntimeError(f"No fue posible validar la sesion con authservice: HTTP {exc.code}") from exc
        except urllib_error.URLError as exc:
            raise RuntimeError(f"No fue posible conectar con authservice: {exc.reason}") from exc
