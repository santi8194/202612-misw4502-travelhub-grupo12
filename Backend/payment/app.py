import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SERVICE_NAME = "payment"


def healthcheck() -> str:
    return "ok"


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self._write_json(200, {"status": healthcheck(), "service": SERVICE_NAME})
            return

        if self.path == "/":
            self._write_json(200, {"message": f"{SERVICE_NAME} service is running"})
            return

        self._write_json(404, {"error": "not_found"})

    def log_message(self, format: str, *args) -> None:
        return

    def _write_json(self, status_code: int, payload: dict[str, str]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run() -> None:
    port = int(os.getenv("PORT", "80"))
    server = ThreadingHTTPServer(("0.0.0.0", port), _Handler)
    server.serve_forever()


if __name__ == "__main__":
    run()
