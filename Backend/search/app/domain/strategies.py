"""Strategy pattern for ranking/sorting search results."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class RankingStrategy(ABC):
    """Abstract base class for ranking strategies.

    Each strategy acts as a Query Builder, producing the ``sort``
    clause that will be injected into the OpenSearch query.
    """

    @abstractmethod
    def build_sort(self) -> List[Dict[str, Any]]:
        """Return the OpenSearch sort clause."""


class PriceFirstStrategy(RankingStrategy):
    """Sort results by ascending base price."""

    def build_sort(self) -> List[Dict[str, Any]]:
        return [{"precio_base": {"order": "asc"}}]
