from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from src.application.transformation_service import PMSDataTransformer
from src.domain.enums import ResourceType
from src.domain.models import SyncBatchEvent, SyncBatchResult, SyncCommand
from src.domain.ports import (
    IdempotencyStorePort,
    InventoryPublisherPort,
    PMSPort,
    RetryQueuePort,
)


class SyncApplicationService:
    def __init__(
        self,
        pms_adapter: PMSPort,
        transformer: PMSDataTransformer,
        inventory_publisher: InventoryPublisherPort,
        idempotency_store: IdempotencyStorePort,
        retry_queue: RetryQueuePort,
        logger,
    ) -> None:
        self._pms_adapter = pms_adapter
        self._transformer = transformer
        self._inventory_publisher = inventory_publisher
        self._idempotency_store = idempotency_store
        self._retry_queue = retry_queue
        self._logger = logger
        self._last_results: dict[ResourceType, SyncBatchResult] = {}

    async def sync_properties(self, trigger: str = "polling") -> SyncBatchResult:
        raw_records = await self._pms_adapter.fetch_properties()
        return await self._dispatch_records(
            resource_type=ResourceType.PROPERTY,
            raw_records=raw_records,
            trigger=trigger,
            source_system=self._pms_adapter.source_system,
            source_event_id=None,
        )

    async def sync_room_types(self, trigger: str = "polling") -> SyncBatchResult:
        raw_records = await self._pms_adapter.fetch_room_types()
        return await self._dispatch_records(
            resource_type=ResourceType.ROOM_TYPE,
            raw_records=raw_records,
            trigger=trigger,
            source_system=self._pms_adapter.source_system,
            source_event_id=None,
        )

    async def sync_availability(self, trigger: str = "polling") -> SyncBatchResult:
        raw_records = await self._pms_adapter.fetch_availability()
        return await self._dispatch_records(
            resource_type=ResourceType.AVAILABILITY,
            raw_records=raw_records,
            trigger=trigger,
            source_system=self._pms_adapter.source_system,
            source_event_id=None,
        )

    async def sync_rates(self, trigger: str = "polling") -> SyncBatchResult:
        raw_records = await self._pms_adapter.fetch_rates()
        return await self._dispatch_records(
            resource_type=ResourceType.RATE,
            raw_records=raw_records,
            trigger=trigger,
            source_system=self._pms_adapter.source_system,
            source_event_id=None,
        )

    async def sync_generated_event(
        self,
        resource_type: ResourceType | None = None,
    ) -> SyncBatchResult:
        event = await self._pms_adapter.generate_event(resource_type=resource_type)
        return await self._process_event(event)

    async def process_webhook_event(
        self,
        resource_type: ResourceType,
        raw_records: list[dict[str, Any]],
        source_event_id: str | None,
        source_system: str,
    ) -> SyncBatchResult:
        event = SyncBatchEvent(
            resource_type=resource_type,
            records=raw_records,
            source_event_id=source_event_id
            or f"{source_system}-{resource_type.value}-{int(datetime.now(tz=timezone.utc).timestamp())}",
            source_system=source_system,
            occurred_at=datetime.now(tz=timezone.utc),
            trigger="webhook",
        )
        return await self._process_event(event)

    def get_status(self) -> dict[str, Any]:
        last_results = {
            resource.value: result.to_dict()
            for resource, result in self._last_results.items()
        }
        return {
            "queue_size": self._retry_queue.size(),
            "last_results": last_results,
        }

    async def _process_event(self, event: SyncBatchEvent) -> SyncBatchResult:
        return await self._dispatch_records(
            resource_type=event.resource_type,
            raw_records=event.records,
            trigger=event.trigger,
            source_system=event.source_system,
            source_event_id=event.source_event_id,
        )

    async def _dispatch_records(
        self,
        resource_type: ResourceType,
        raw_records: list[dict[str, Any]],
        trigger: str,
        source_system: str,
        source_event_id: str | None,
    ) -> SyncBatchResult:
        processed = len(raw_records)
        sent = 0
        skipped = 0
        queued = 0
        failed = 0
        event_id = source_event_id

        for raw_record in raw_records:
            command = None
            try:
                payload = self._transformer.transform(resource_type, raw_record)
                command = self._build_command(
                    resource_type=resource_type,
                    raw_record=raw_record,
                    payload=payload,
                    source_system=source_system,
                    trigger=trigger,
                    batch_event_id=source_event_id,
                )
                if event_id is None:
                    event_id = command.source_event_id
                is_new = await self._idempotency_store.register(command.idempotency_key)
                if not is_new:
                    skipped += 1
                    self._logger.info(
                        "sync.duplicate_skipped",
                        extra={
                            "resource_type": resource_type.value,
                            "idempotency_key": command.idempotency_key,
                            "source_event_id": command.source_event_id,
                            "trigger": trigger,
                        },
                    )
                    continue

                await self._inventory_publisher.publish(command)
                sent += 1
                self._logger.info(
                    "sync.command_sent",
                    extra={
                        "resource_type": resource_type.value,
                        "idempotency_key": command.idempotency_key,
                        "source_event_id": command.source_event_id,
                        "trigger": trigger,
                        "target_path": resource_type.inventory_sync_path,
                    },
                )
            except Exception as exc:
                failed += 1
                if command is not None:
                    await self._retry_queue.enqueue(command, reason=str(exc))
                    queued += 1
                self._logger.error(
                    "sync.command_failed",
                    extra={
                        "resource_type": resource_type.value,
                        "source_event_id": event_id,
                        "trigger": trigger,
                        "error": str(exc),
                    },
                )

        result = SyncBatchResult(
            resource_type=resource_type,
            trigger=trigger,
            source_event_id=event_id,
            processed=processed,
            sent=sent,
            skipped=skipped,
            queued=queued,
            failed=failed,
            completed_at=datetime.now(tz=timezone.utc),
        )
        self._last_results[resource_type] = result
        self._logger.info("sync.completed", extra=result.log_context())
        return result

    def _build_command(
        self,
        resource_type: ResourceType,
        raw_record: dict[str, Any],
        payload: dict[str, Any],
        source_system: str,
        trigger: str,
        batch_event_id: str | None,
    ) -> SyncCommand:
        source_event_id = batch_event_id or raw_record.get("event_id") or self._hash_payload(
            {
                "resourceType": resource_type.value,
                "payload": payload,
                "sourceSystem": source_system,
            }
        )[:24]
        idempotency_key = self._hash_payload(
            {
                "sourceEventId": source_event_id,
                "resourceType": resource_type.value,
                "payload": payload,
            }
        )
        return SyncCommand(
            resource_type=resource_type,
            payload=payload,
            source_system=source_system,
            idempotency_key=idempotency_key,
            source_event_id=source_event_id,
            occurred_at=datetime.now(tz=timezone.utc),
            trigger=trigger,
        )

    def _hash_payload(self, value: dict[str, Any]) -> str:
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
