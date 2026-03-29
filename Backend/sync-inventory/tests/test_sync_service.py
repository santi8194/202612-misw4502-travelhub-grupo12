import asyncio

from src.application.sync_service import SyncApplicationService
from src.application.transformation_service import PMSDataTransformer
from src.domain.enums import ResourceType
from src.infrastructure.adapters.mock_pms_adapter import MockPMSAdapter
from src.infrastructure.idempotency.in_memory_store import (
    InMemoryIdempotencyStore,
)
from src.infrastructure.logging import configure_logging
from src.infrastructure.queue.in_memory_retry_queue import (
    InMemoryRetryQueue,
)


class FakePublisher:
    def __init__(self) -> None:
        self.commands = []

    async def publish(self, command) -> None:
        self.commands.append(command)


def test_sync_properties_is_idempotent() -> None:
    async def scenario() -> None:
        publisher = FakePublisher()
        logger = configure_logging("INFO")
        service = SyncApplicationService(
            pms_adapter=MockPMSAdapter(seed=7),
            transformer=PMSDataTransformer(),
            inventory_publisher=publisher,
            idempotency_store=InMemoryIdempotencyStore(),
            retry_queue=InMemoryRetryQueue(logger=logger),
            logger=logger,
        )

        first = await service.sync_properties(trigger="test")
        second = await service.sync_properties(trigger="test")

        assert first.processed == 2
        assert first.sent == 2
        assert second.sent == 0
        assert second.skipped == 2
        assert publisher.commands[0].payload["idPropiedad"] == "f47ac10b-58cc-4372-a567-0e02b2c3d479"
        assert publisher.commands[0].payload["ubicacion"]["coordenadas"]["lat"] == 10.42

    asyncio.run(scenario())


def test_room_type_includes_media_and_amenities() -> None:
    async def scenario() -> None:
        publisher = FakePublisher()
        logger = configure_logging("INFO")
        service = SyncApplicationService(
            pms_adapter=MockPMSAdapter(seed=11),
            transformer=PMSDataTransformer(),
            inventory_publisher=publisher,
            idempotency_store=InMemoryIdempotencyStore(),
            retry_queue=InMemoryRetryQueue(logger=logger),
            logger=logger,
        )

        result = await service.sync_room_types(trigger="test")

        assert result.sent == 3
        assert publisher.commands[0].payload["amenidades"][0]["idAmenidad"] == "am3n-1122-3344"
        assert publisher.commands[0].payload["media"][0]["tipo"] == "IMAGEN_GALERIA"

    asyncio.run(scenario())


def test_webhook_event_uses_precio_base_shape() -> None:
    async def scenario() -> None:
        publisher = FakePublisher()
        logger = configure_logging("INFO")
        service = SyncApplicationService(
            pms_adapter=MockPMSAdapter(seed=9),
            transformer=PMSDataTransformer(),
            inventory_publisher=publisher,
            idempotency_store=InMemoryIdempotencyStore(),
            retry_queue=InMemoryRetryQueue(logger=logger),
            logger=logger,
        )

        result = await service.process_webhook_event(
            resource_type=ResourceType.RATE,
            source_event_id="custom-event-1",
            source_system="partner-pms",
            raw_records=[
                {
                    "property_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                    "category_id": "c987d654-1111-4ef9-a222-1234567890ab",
                    "codigo_mapeo_pms": "ROOM-DLX-01",
                    "precio_base": {"monto": 355000.0, "moneda": "COP"},
                    "updated_at": "2026-03-29T17:00:00+00:00",
                }
            ],
        )

        assert result.sent == 1
        assert publisher.commands[0].source_event_id == "custom-event-1"
        assert publisher.commands[0].to_http_payload()["resourceType"] == "rate"
        assert publisher.commands[0].payload["precioBase"]["moneda"] == "COP"

    asyncio.run(scenario())
