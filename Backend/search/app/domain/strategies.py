"""Patrón Strategy para el ordenamiento de resultados de búsqueda."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class RankingStrategy(ABC):
    """Clase base abstracta para las estrategias de ordenamiento.

    Cada estrategia actúa como un Query Builder, produciendo la cláusula
    de ordenamiento para el motor activo (OpenSearch o PostgreSQL).
    """

    @abstractmethod
    def build_sort(self) -> List[Dict[str, Any]]:
        """Retorna la cláusula ``sort`` de OpenSearch."""

    @abstractmethod
    def build_sql_sort(self) -> str:
        """Retorna la cláusula SQL ``ORDER BY`` (sin la palabra clave 'ORDER BY')."""


class PriceFirstStrategy(RankingStrategy):
    """Sort results by ascending base price."""

    def build_sort(self) -> List[Dict[str, Any]]:
        return [{"precio_base": {"order": "asc"}}]

    def build_sql_sort(self) -> str:
        return "precio_base ASC"
