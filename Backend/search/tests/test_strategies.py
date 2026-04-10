"""Pruebas unitarias para las estrategias de ordenamiento."""

from __future__ import annotations

from app.domain.strategies import PriceFirstStrategy, RankingStrategy


class TestPriceFirstStrategy:
    def test_is_ranking_strategy(self):
        strategy = PriceFirstStrategy()
        assert isinstance(strategy, RankingStrategy)

    def test_build_sort_returns_price_asc(self):
        strategy = PriceFirstStrategy()
        result = strategy.build_sort()
        assert result == [{"precio_base": {"order": "asc"}}]

    def test_build_sql_sort_returns_price_asc(self):
        """Verifica que el ORDER BY SQL sea correcto para precio ascendente."""
        strategy = PriceFirstStrategy()
        assert strategy.build_sql_sort() == "precio_base ASC"

    def test_build_sort_returns_list(self):
        strategy = PriceFirstStrategy()
        result = strategy.build_sort()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_build_sort_is_idempotent(self):
        strategy = PriceFirstStrategy()
        assert strategy.build_sort() == strategy.build_sort()


class TestCustomStrategy:
    """Verify the strategy interface can be extended."""

    def test_custom_strategy_implementation(self):
        """Verifica que se puede crear una estrategia personalizada implementando ambos métodos."""
        class RatingFirstStrategy(RankingStrategy):
            def build_sort(self):
                return [{"rating_promedio": {"order": "desc"}}]

            def build_sql_sort(self):
                return "rating_promedio DESC"

        strategy = RatingFirstStrategy()
        assert isinstance(strategy, RankingStrategy)
        assert strategy.build_sort() == [{"rating_promedio": {"order": "desc"}}]
        assert strategy.build_sql_sort() == "rating_promedio DESC"

    def test_abstract_base_cannot_be_instantiated(self):
        import pytest

        with pytest.raises(TypeError):
            RankingStrategy()  # type: ignore[abstract]
