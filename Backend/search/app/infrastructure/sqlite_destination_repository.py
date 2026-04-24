"""SQLite adapter for destination autocomplete in local runs."""

from __future__ import annotations

import asyncio
import sqlite3
from typing import List

from app.application.ports import DestinationRepository


class SQLiteDestinationRepository(DestinationRepository):
    """SQLite-backed implementation of the destination autocomplete port."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    async def autocomplete(self, prefix: str) -> List[dict]:
        return await asyncio.to_thread(self._autocomplete_sync, prefix)

    def _autocomplete_sync(self, prefix: str) -> List[dict]:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        try:
            rows = connection.execute(
                """
                SELECT ciudad, estado_provincia, pais
                FROM destinos
                WHERE ciudad_lower LIKE ? || '%'
                ORDER BY ciudad_lower
                LIMIT 10
                """,
                (prefix.lower(),),
            ).fetchall()
            return [
                {
                    "ciudad": row["ciudad"],
                    "estado_provincia": row["estado_provincia"],
                    "pais": row["pais"],
                }
                for row in rows
            ]
        finally:
            connection.close()
