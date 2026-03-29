from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.models import SyncCommand
from src.domain.ports import InventoryPublisherPort


@dataclass(slots=True)
class QueueItem:
    command: SyncCommand
    reason: str
    attempts: int = 0
    queued_at: str = field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat()
    )


class InMemoryRetryQueue:
    def __init__(self, logger, max_attempts: int = 3) -> None:
        self._logger = logger
        self._max_attempts = max_attempts
        self._items: deque[QueueItem] = deque()
        self._lock = asyncio.Lock()

    async def enqueue(self, command: SyncCommand, reason: str) -> None:
        async with self._lock:
            self._items.append(QueueItem(command=command, reason=reason))
            self._logger.warning(
                "retry_queue.enqueued",
                extra={
                    "resource_type": command.resource_type.value,
                    "source_event_id": command.source_event_id,
                    "reason": reason,
                    "queue_size": len(self._items),
                },
            )

    async def drain(self, publisher: InventoryPublisherPort) -> int:
        async with self._lock:
            if not self._items:
                return 0
            items = list(self._items)
            self._items.clear()

        requeued = 0
        for item in items:
            try:
                await publisher.publish(item.command)
                self._logger.info(
                    "retry_queue.published",
                    extra={
                        "resource_type": item.command.resource_type.value,
                        "source_event_id": item.command.source_event_id,
                        "attempts": item.attempts + 1,
                    },
                )
            except Exception as exc:
                item.attempts += 1
                if item.attempts < self._max_attempts:
                    async with self._lock:
                        self._items.append(item)
                        requeued += 1
                self._logger.error(
                    "retry_queue.publish_failed",
                    extra={
                        "resource_type": item.command.resource_type.value,
                        "source_event_id": item.command.source_event_id,
                        "attempts": item.attempts,
                        "error": str(exc),
                    },
                )
        return requeued

    def size(self) -> int:
        return len(self._items)
