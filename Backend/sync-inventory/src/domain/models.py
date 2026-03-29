from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.domain.enums import ResourceType


@dataclass(frozen=True)
class SyncCommand:
    resource_type: ResourceType
    payload: dict[str, Any]
    source_system: str
    idempotency_key: str
    source_event_id: str
    occurred_at: datetime
    trigger: str

    def to_http_payload(self) -> dict[str, Any]:
        resource_type = (
            "roomType" if self.resource_type is ResourceType.ROOM_TYPE else self.resource_type.value
        )
        return {
            "eventId": self.source_event_id,
            "idempotencyKey": self.idempotency_key,
            "resourceType": resource_type,
            "sourceSystem": self.source_system,
            "trigger": self.trigger,
            "occurredAt": self.occurred_at.isoformat(),
            "payload": self.payload,
        }


@dataclass(frozen=True)
class SyncBatchEvent:
    resource_type: ResourceType
    records: list[dict[str, Any]]
    source_event_id: str
    source_system: str
    occurred_at: datetime
    trigger: str


@dataclass(frozen=True)
class SyncBatchResult:
    resource_type: ResourceType
    trigger: str
    source_event_id: str | None
    processed: int
    sent: int
    skipped: int
    queued: int
    failed: int
    completed_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_type": self.resource_type.value,
            "trigger": self.trigger,
            "source_event_id": self.source_event_id,
            "processed": self.processed,
            "sent": self.sent,
            "skipped": self.skipped,
            "queued": self.queued,
            "failed": self.failed,
            "completed_at": self.completed_at.isoformat(),
        }

    def log_context(self) -> dict[str, Any]:
        return self.to_dict()
