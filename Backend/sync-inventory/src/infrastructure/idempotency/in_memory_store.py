from __future__ import annotations

import asyncio
from collections import OrderedDict
from datetime import datetime, timezone


class InMemoryIdempotencyStore:
    def __init__(self, max_items: int = 10000) -> None:
        self._max_items = max_items
        self._entries: OrderedDict[str, str] = OrderedDict()
        self._lock = asyncio.Lock()

    async def register(self, key: str) -> bool:
        async with self._lock:
            if key in self._entries:
                return False

            self._entries[key] = datetime.now(tz=timezone.utc).isoformat()
            if len(self._entries) > self._max_items:
                self._entries.popitem(last=False)
            return True
