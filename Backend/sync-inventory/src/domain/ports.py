from __future__ import annotations

from typing import Protocol

from src.domain.enums import ResourceType
from src.domain.models import SyncBatchEvent, SyncCommand


class PMSPort(Protocol):
    source_system: str

    async def fetch_properties(self) -> list[dict]:
        ...

    async def fetch_room_types(self) -> list[dict]:
        ...

    async def fetch_availability(self) -> list[dict]:
        ...

    async def fetch_rates(self) -> list[dict]:
        ...

    async def generate_event(
        self,
        resource_type: ResourceType | None = None,
    ) -> SyncBatchEvent:
        ...


class InventoryPublisherPort(Protocol):
    async def publish(self, command: SyncCommand) -> None:
        ...


class IdempotencyStorePort(Protocol):
    async def register(self, key: str) -> bool:
        ...


class RetryQueuePort(Protocol):
    async def enqueue(self, command: SyncCommand, reason: str) -> None:
        ...

    async def drain(self, publisher: InventoryPublisherPort) -> int:
        ...

    def size(self) -> int:
        ...
