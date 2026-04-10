from fastapi import FastAPI

SERVICE_NAME = "booking"


def healthcheck() -> str:
    return "ok"


app = FastAPI(title="Booking Service", version="1.0.0")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": healthcheck()}


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": healthcheck()}
