from __future__ import annotations

import asyncio
from contextlib import suppress

from src.application.sync_service import SyncApplicationService
from src.config import Settings
from src.domain.enums import ResourceType
from src.domain.ports import InventoryPublisherPort
from src.infrastructure.queue.in_memory_retry_queue import InMemoryRetryQueue


class SyncScheduler:
    def __init__(
        self,
        settings: Settings,
        sync_service: SyncApplicationService,
        retry_queue: InMemoryRetryQueue,
        inventory_publisher: InventoryPublisherPort,
        logger,
    ) -> None:
        self._settings = settings
        self._sync_service = sync_service
        self._retry_queue = retry_queue
        self._inventory_publisher = inventory_publisher
        self._logger = logger
        self._tasks: list[asyncio.Task] = []
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        self._started = True

        if self._settings.polling_enabled:
            self._tasks.extend(
                [
                    asyncio.create_task(
                        self._poll_loop(
                            "property-poll",
                            self._settings.property_poll_interval_seconds,
                            self._sync_service.sync_properties,
                        )
                    ),
                    asyncio.create_task(
                        self._poll_loop(
                            "room-type-poll",
                            self._settings.room_type_poll_interval_seconds,
                            self._sync_service.sync_room_types,
                        )
                    ),
                    asyncio.create_task(
                        self._poll_loop(
                            "availability-poll",
                            self._settings.availability_poll_interval_seconds,
                            self._sync_service.sync_availability,
                        )
                    ),
                    asyncio.create_task(
                        self._poll_loop(
                            "rate-poll",
                            self._settings.rate_poll_interval_seconds,
                            self._sync_service.sync_rates,
                        )
                    ),
                ]
            )

        if self._settings.event_simulation_enabled:
            self._tasks.append(
                asyncio.create_task(
                    self._event_loop(self._settings.event_simulation_interval_seconds)
                )
            )

        self._tasks.append(
            asyncio.create_task(
                self._retry_loop(self._settings.queue_drain_interval_seconds)
            )
        )

    async def stop(self) -> None:
        if not self._started:
            return
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            with suppress(asyncio.CancelledError):
                await task
        self._tasks.clear()
        self._started = False

    async def _poll_loop(self, name: str, interval_seconds: int, callback) -> None:
        while True:
            try:
                await callback(trigger="polling")
            except Exception as exc:
                self._logger.error(
                    "scheduler.poll_failed",
                    extra={"loop": name, "error": str(exc)},
                )
            await asyncio.sleep(interval_seconds)

    async def _event_loop(self, interval_seconds: int) -> None:
        cycle = list(ResourceType)
        index = 0
        while True:
            resource_type = cycle[index % len(cycle)]
            index += 1
            try:
                await self._sync_service.sync_generated_event(resource_type=resource_type)
            except Exception as exc:
                self._logger.error(
                    "scheduler.event_failed",
                    extra={
                        "resource_type": resource_type.value,
                        "error": str(exc),
                    },
                )
            await asyncio.sleep(interval_seconds)

    async def _retry_loop(self, interval_seconds: int) -> None:
        while True:
            try:
                await self._retry_queue.drain(self._inventory_publisher)
            except Exception as exc:
                self._logger.error(
                    "scheduler.retry_failed",
                    extra={"error": str(exc)},
                )
            await asyncio.sleep(interval_seconds)
