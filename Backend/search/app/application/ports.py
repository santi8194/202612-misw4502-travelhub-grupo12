"""Output ports (repository interfaces) for the application layer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from app.domain.entities import Hospedaje
from app.domain.strategies import RankingStrategy


class HospedajeRepository(ABC):
    """Port for searching accommodations in the persistence layer."""

    @abstractmethod
    async def buscar(
        self,
        ciudad: str,
        estado_provincia: str,
        pais: str,
        fecha_inicio: date,
        fecha_fin: date,
        huespedes: int,
        strategy: RankingStrategy,
    ) -> List[Hospedaje]:
        """Search accommodations matching the given criteria.

        Parameters
        ----------
        ciudad:
            Exact city name.
        estado_provincia:
            State or province (may be empty).
        pais:
            Exact country name.
        fecha_inicio:
            Check-in date (inclusive).
        fecha_fin:
            Check-out date (inclusive).
        huespedes:
            Minimum number of guests that must be available each day.
        strategy:
            Ranking strategy providing the sort clause.

        Returns
        -------
        List of matching :class:`Hospedaje` entities.
        """
