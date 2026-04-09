"""Adaptador PostgreSQL para consultas de autocompletado de destinos."""

from __future__ import annotations

from typing import List

import asyncpg

from app.application.ports import DestinationRepository


class PostgresDestinationRepository(DestinationRepository):
    """Implementación del repositorio de destinos respaldado por PostgreSQL.

    Consulta la tabla search.destinos usando un índice de prefijo
    sobre ciudad_lower con varchar_pattern_ops para búsquedas eficientes.
    """

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def autocomplete(self, prefix: str) -> List[dict]:
        """
        Retorna sugerencias de destinos cuyo nombre de ciudad comienza con *prefix*.

        Parámetros
        ----------
        prefix:
            Texto ingresado por el usuario (mín 3 caracteres).
            Convertido a minúsculas internamente para aprovechar el índice.

        Retorna
        -------
        Lista de diccionarios con claves ``ciudad``, ``estado_provincia``, ``pais``.
        Lista vacía si no hay coincidencias. Máximo 10 resultados.
        """
        # Normalizar a minúsculas para usar el índice varchar_pattern_ops
        prefix_lower = prefix.lower()

        query = """
            SELECT ciudad, estado_provincia, pais
            FROM search.destinos
            WHERE ciudad_lower LIKE $1 || '%'
            ORDER BY ciudad_lower
            LIMIT 10
        """

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, prefix_lower)

        # Convertir asyncpg.Records a diccionarios planos
        return [
            {
                "ciudad": row["ciudad"],
                "estado_provincia": row["estado_provincia"],
                "pais": row["pais"],
            }
            for row in rows
        ]
