from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WebhookRequest(BaseModel):
    event_id: str | None = Field(default=None)
    source_system: str = Field(default="mock-pms")
    records: list[dict[str, Any]] = Field(default_factory=list)


class SyncResponse(BaseModel):
    resource_type: str
    trigger: str
    source_event_id: str | None = None
    processed: int
    sent: int
    skipped: int
    queued: int
    failed: int
    completed_at: str


class SyncStatusResponse(BaseModel):
    queue_size: int
    last_results: dict[str, dict[str, Any]]
