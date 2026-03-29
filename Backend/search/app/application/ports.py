"""Output ports (repository interfaces) for the application layer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from app.domain.entities import Hospedaje
from app.domain.strategies import RankingStrategy


class HospedajeRepository(ABC):
    """
    Puerto (Interfaz) para la búsqueda de hospedajes en la capa de persistencia.
    """

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
        """
        Busca hospedajes que coincidan con los criterios dados.

        Parámetros
        ----------
        ciudad:
            Nombre exacto de la ciudad.
        estado_provincia:
            Estado o provincia (puede estar vacío).
        pais:
            Nombre exacto del país.
        fecha_inicio:
            Fecha de entrada (inclusiva).
        fecha_fin:
            Fecha de salida (inclusiva).
        huespedes:
            Número mínimo de huéspedes que debe estar disponible cada día.
        strategy:
            Estrategia de ranking que provee la cláusula de ordenamiento.

        Retorna
        -------
        Lista de entidades :class:`Hospedaje` coincidentes.
        """


class DestinationRepository(ABC):
    """
    Puerto (Interfaz) para sugerencias de autocompletado de destinos.
    """

    @abstractmethod
    async def autocomplete(self, prefix: str) -> List[dict]:
        """
        Retorna sugerencias de destinos cuyo nombre de ciudad comienza con *prefix*.

        Parámetros
        ----------
        prefix:
            Texto (mínimo 3 caracteres).

        Retorna
        -------
        Lista de diccionarios con claves ``ciudad``, ``estado_provincia``, ``pais``.
        """
