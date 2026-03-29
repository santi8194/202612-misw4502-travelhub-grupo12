"""Redis adapter for destination autocomplete queries."""

from __future__ import annotations

import json
from typing import List

from redis.asyncio import Redis


DEST_INDEX_KEY = "search:destinations:index"
DEST_DATA_KEY = "search:destinations:data"


class RedisDestinationRepository:
    """Reads destination suggestions from Redis using lexicographic range queries.

    Data structures expected in Redis:
    - Sorted Set ``search:destinations:index`` with members ``{ciudad_lower}:{id}``
      and score 0 (pure lexicographic ordering).
    - Hash ``search:destinations:data`` with field ``{id}`` and value as
      JSON-encoded ``{"ciudad": ..., "estado_provincia": ..., "pais": ...}``.
    """

    def __init__(self, client: Redis) -> None:
        self._client = client

    async def autocomplete(self, prefix: str) -> List[dict]:
        """Return destination dicts whose city name starts with *prefix*.

        Parameters
        ----------
        prefix:
            User-typed text (min 3 chars). Converted to lowercase internally.

        Returns
        -------
        List of dicts with keys ``ciudad``, ``estado_provincia``, ``pais``.
        Empty list if no matches.
        """
        prefix_lower = prefix.lower()

        # 1. ZRANGEBYLEX — lexicographic range [prefix, prefix\xff)
        members: list[str] = await self._client.zrangebylex(
            DEST_INDEX_KEY,
            f"[{prefix_lower}",
            f"[{prefix_lower}\xff",
        )

        if not members:
            return []

        # 2. Extract IDs from "ciudad_lower:id" format
        ids = [m.split(":", 1)[1] for m in members]

        # 3. HMGET — fetch JSON payloads
        raw_values = await self._client.hmget(DEST_DATA_KEY, *ids)

        # 4. Parse JSON, skip any None values
        results: list[dict] = []
        for raw in raw_values:
            if raw is not None:
                results.append(json.loads(raw))

        return results
