from __future__ import annotations

import asyncio

import httpx

from src.domain.models import SyncCommand


class InventoryServiceClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        max_retries: int,
        retry_delay_seconds: float,
        logger,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._retry_delay_seconds = retry_delay_seconds
        self._logger = logger
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

    async def publish(self, command: SyncCommand) -> None:
        url = f"{self._base_url}{command.resource_type.inventory_sync_path}"
        headers = {
            "X-Idempotency-Key": command.idempotency_key,
            "X-Source-Event-Id": command.source_event_id,
        }

        for attempt in range(1, self._max_retries + 2):
            try:
                response = await self._client.post(
                    url,
                    json=command.to_http_payload(),
                    headers=headers,
                )
                response.raise_for_status()
                return
            except httpx.HTTPStatusError as exc:
                retryable = exc.response.status_code >= 500
                if attempt > self._max_retries or not retryable:
                    raise
                self._logger.warning(
                    "inventory.publish_retry",
                    extra={
                        "url": url,
                        "attempt": attempt,
                        "status_code": exc.response.status_code,
                        "source_event_id": command.source_event_id,
                    },
                )
            except httpx.HTTPError as exc:
                if attempt > self._max_retries:
                    raise
                self._logger.warning(
                    "inventory.publish_retry",
                    extra={
                        "url": url,
                        "attempt": attempt,
                        "error": str(exc),
                        "source_event_id": command.source_event_id,
                    },
                )

            await asyncio.sleep(self._retry_delay_seconds * attempt)

    async def close(self) -> None:
        await self._client.aclose()
