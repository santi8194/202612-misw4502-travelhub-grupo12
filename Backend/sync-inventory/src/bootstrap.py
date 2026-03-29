from __future__ import annotations

from dataclasses import dataclass

from src.application.sync_service import SyncApplicationService
from src.application.transformation_service import PMSDataTransformer
from src.config import Settings
from src.domain.ports import InventoryPublisherPort
from src.infrastructure.adapters.mock_pms_adapter import MockPMSAdapter
from src.infrastructure.clients.inventory_service_client import (
    InventoryServiceClient,
)
from src.infrastructure.idempotency.in_memory_store import (
    InMemoryIdempotencyStore,
)
from src.infrastructure.logging import configure_logging
from src.infrastructure.queue.in_memory_retry_queue import (
    InMemoryRetryQueue,
)
from src.infrastructure.scheduling.sync_scheduler import SyncScheduler


@dataclass(slots=True)
class ServiceContainer:
    settings: Settings
    logger: object
    pms_adapter: MockPMSAdapter
    transformer: PMSDataTransformer
    idempotency_store: InMemoryIdempotencyStore
    retry_queue: InMemoryRetryQueue
    inventory_publisher: InventoryPublisherPort
    sync_service: SyncApplicationService
    scheduler: SyncScheduler


def build_container(
    settings: Settings | None = None,
    inventory_publisher: InventoryPublisherPort | None = None,
) -> ServiceContainer:
    resolved_settings = settings or Settings()
    logger = configure_logging(resolved_settings.log_level)
    pms_adapter = MockPMSAdapter(seed=resolved_settings.pms_random_seed)
    transformer = PMSDataTransformer()
    idempotency_store = InMemoryIdempotencyStore()
    retry_queue = InMemoryRetryQueue(
        logger=logger,
        max_attempts=resolved_settings.queue_max_attempts,
    )
    publisher = inventory_publisher or InventoryServiceClient(
        base_url=resolved_settings.inventory_service_base_url,
        timeout_seconds=resolved_settings.request_timeout_seconds,
        max_retries=resolved_settings.http_max_retries,
        retry_delay_seconds=resolved_settings.http_retry_delay_seconds,
        logger=logger,
    )
    sync_service = SyncApplicationService(
        pms_adapter=pms_adapter,
        transformer=transformer,
        inventory_publisher=publisher,
        idempotency_store=idempotency_store,
        retry_queue=retry_queue,
        logger=logger,
    )
    scheduler = SyncScheduler(
        settings=resolved_settings,
        sync_service=sync_service,
        retry_queue=retry_queue,
        inventory_publisher=publisher,
        logger=logger,
    )
    return ServiceContainer(
        settings=resolved_settings,
        logger=logger,
        pms_adapter=pms_adapter,
        transformer=transformer,
        idempotency_store=idempotency_store,
        retry_queue=retry_queue,
        inventory_publisher=publisher,
        sync_service=sync_service,
        scheduler=scheduler,
    )
