"""Redis adapter for destination autocomplete queries."""

from __future__ import annotations

import json
from typing import List

from redis.asyncio import Redis


from app.application.ports import DestinationRepository
from app.infrastructure.redis_keys import DEST_INDEX_KEY, DEST_DATA_KEY


class RedisDestinationRepository(DestinationRepository):
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
        """
        Retorna los diccionarios de destino cuyo nombre de ciudad comienza con *prefix*.

        Parámetros
        ----------
        prefix:
            Texto ingresado por el usuario (mín 3 caracteres). Comvertido a minúsculas internamente.

        Retorna
        -------
        Lista de diccionarios con claves ``ciudad``, ``estado_provincia``, ``pais``.
        Lista vacía si no hay coincidencias.
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
