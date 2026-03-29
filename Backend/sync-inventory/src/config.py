from __future__ import annotations

import os
from dataclasses import dataclass


def _read_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    service_name: str = "sync-inventory"
    inventory_service_base_url: str = os.getenv(
        "INVENTORY_SERVICE_BASE_URL",
        "http://localhost:8000",
    )
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "5"))
    http_max_retries: int = int(os.getenv("HTTP_MAX_RETRIES", "2"))
    http_retry_delay_seconds: float = float(os.getenv("HTTP_RETRY_DELAY_SECONDS", "1"))
    queue_max_attempts: int = int(os.getenv("QUEUE_MAX_ATTEMPTS", "3"))
    queue_drain_interval_seconds: int = int(os.getenv("QUEUE_DRAIN_INTERVAL_SECONDS", "10"))
    property_poll_interval_seconds: int = int(
        os.getenv("PROPERTY_POLL_INTERVAL_SECONDS", "30")
    )
    room_type_poll_interval_seconds: int = int(
        os.getenv("ROOM_TYPE_POLL_INTERVAL_SECONDS", "45")
    )
    availability_poll_interval_seconds: int = int(
        os.getenv("AVAILABILITY_POLL_INTERVAL_SECONDS", "20")
    )
    rate_poll_interval_seconds: int = int(os.getenv("RATE_POLL_INTERVAL_SECONDS", "25"))
    event_simulation_interval_seconds: int = int(
        os.getenv("EVENT_SIMULATION_INTERVAL_SECONDS", "15")
    )
    polling_enabled: bool = _read_bool("POLLING_ENABLED", True)
    event_simulation_enabled: bool = _read_bool("EVENT_SIMULATION_ENABLED", True)
    pms_random_seed: int = int(os.getenv("PMS_RANDOM_SEED", "42"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
