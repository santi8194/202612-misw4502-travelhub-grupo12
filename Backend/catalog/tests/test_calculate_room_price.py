import pytest
from datetime import date
from decimal import Decimal
from uuid import uuid4
from unittest.mock import Mock

from modules.catalog.application.queries.calculate_room_price import CalculateRoomPrice
from modules.catalog.domain.entities import (
    CategoriaHabitacion,
    ConfiguracionImpuestosPais,
    VODinero,
    VORegla,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def repo():
    return Mock()


@pytest.fixture
def categoria():
    return CategoriaHabitacion(
        id_categoria=uuid4(),
        codigo_mapeo_pms="TEST-01",
        nombre_comercial="Test Room",
        descripcion="Test desc",
        capacidad_pax=2,
        politica_cancelacion=VORegla(dias_anticipacion=2, porcentaje_penalidad=Decimal("10")),
        precio_base=VODinero(monto=Decimal("100"), moneda="USD", cargo_servicio=Decimal("10")),
        tarifa_fin_de_semana=VODinero(monto=Decimal("120"), moneda="USD", cargo_servicio=Decimal("12")),
        tarifa_temporada_alta=VODinero(monto=Decimal("150"), moneda="USD", cargo_servicio=Decimal("15")),
    )


@pytest.fixture
def tax_cop():
    return ConfiguracionImpuestosPais(
        pais="Colombia",
        moneda="COP",
        simbolo_moneda="$",
        locale="es_CO",
        decimales=0,
        tasa_usd=Decimal("4200"),
        impuesto_nombre="IVA",
        impuesto_tasa=Decimal("0.19"),
    )


# ── Helpers para montar el mock ───────────────────────────────────────────────


def _setup_repo(repo, categoria, tax_config):
    repo.obtain_category_by_id.return_value = categoria
    repo.obtain_tax_config_by_country.return_value = tax_config
    # Precio origen USD → no consulta la BD para la tasa de origen
    repo.obtain_tax_config_by_currency.return_value = None


# ── Tests de resolución de tarifa ─────────────────────────────────────────────


def test_tarifa_base_temporada_baja(repo, categoria, tax_cop):
    """Miércoles de octubre = temporada baja, día laboral → BASE."""
    _setup_repo(repo, categoria, tax_cop)
    result = CalculateRoomPrice(repo).execute(
        categoria.id_categoria, date(2026, 10, 14), date(2026, 10, 16), "Colombia"
    )
    # 100 USD × 4200 = 420 000 COP/noche; 2 noches
    # Subtotal = 840 000; IVA 19 % = 159 600; cargo = 10 × 4200 = 42 000
    # Impuestos y cargos = 201 600; Total = 1 041 600
    assert result["tipo_tarifa"] == "BASE"
    assert result["precio_por_noche"] == 420_000.0
    assert result["noches"] == 2
    assert result["subtotal"] == 840_000.0
    assert result["impuestos_y_cargos"] == 201_600.0
    assert result["total"] == 1_041_600.0
    assert result["moneda"] == "COP"
    assert result["simbolo_moneda"] == "$"
    assert result["impuesto_nombre"] == "IVA"


def test_tarifa_fin_de_semana(repo, categoria, tax_cop):
    """Viernes de octubre = temporada baja, fin de semana → FIN_DE_SEMANA."""
    _setup_repo(repo, categoria, tax_cop)
    result = CalculateRoomPrice(repo).execute(
        categoria.id_categoria, date(2026, 10, 16), date(2026, 10, 17), "Colombia"
    )
    # 120 USD × 4200 = 504 000 COP/noche; 1 noche
    # Subtotal = 504 000; IVA 19 % = 95 760; cargo = 12 × 4200 = 50 400
    # Impuestos y cargos = 146 160; Total = 650 160
    assert result["tipo_tarifa"] == "FIN_DE_SEMANA"
    assert result["precio_por_noche"] == 504_000.0
    assert result["total"] == 650_160.0


def test_tarifa_temporada_alta(repo, categoria, tax_cop):
    """Diciembre = temporada alta (prevalece sobre fin de semana) → TEMPORADA_ALTA."""
    _setup_repo(repo, categoria, tax_cop)
    result = CalculateRoomPrice(repo).execute(
        categoria.id_categoria, date(2026, 12, 24), date(2026, 12, 25), "Colombia"
    )
    # 150 USD × 4200 = 630 000 COP/noche
    assert result["tipo_tarifa"] == "TEMPORADA_ALTA"
    assert result["precio_por_noche"] == 630_000.0


def test_conversion_cruzada_monedas(repo, categoria, tax_cop):
    """Categoría en MXN, usuario en Colombia (COP) → doble conversión cruzada."""
    # Modificar categoría a MXN
    categoria.precio_base = VODinero(monto=Decimal("100"), moneda="MXN", cargo_servicio=Decimal("10"))
    
    # Configurar mock para que obtain_tax_config_by_currency("MXN") devuelva tasa 20.0
    tax_mxn = ConfiguracionImpuestosPais(
        pais="México",
        moneda="MXN",
        simbolo_moneda="$",
        locale="es_MX",
        decimales=2,
        tasa_usd=Decimal("20.0"),
        impuesto_nombre="IVA",
        impuesto_tasa=Decimal("0.16"),
    )
    
    repo.obtain_category_by_id.return_value = categoria
    repo.obtain_tax_config_by_country.return_value = tax_cop
    # Para la conversión cruzada, el query debe obtener la tasa de MXN
    repo.obtain_tax_config_by_currency.return_value = tax_mxn

    result = CalculateRoomPrice(repo).execute(
        categoria.id_categoria, date(2026, 10, 14), date(2026, 10, 15), "Colombia"
    )
    
    # Conversión: 100 MXN / 20.0 (tasa MXN) = 5.0 USD
    # 5.0 USD * 4200 (tasa COP) = 21000 COP
    assert result["precio_por_noche"] == 21_000.0


# ── Test de fallback sin configuración de país ────────────────────────────────


def test_fallback_sin_tax_config(repo, categoria):
    """País desconocido → sin conversión, sin impuesto, moneda original."""
    repo.obtain_category_by_id.return_value = categoria
    repo.obtain_tax_config_by_country.return_value = None

    result = CalculateRoomPrice(repo).execute(
        categoria.id_categoria, date(2026, 10, 14), date(2026, 10, 15), "Neverland"
    )
    # Sin config: 1 noche, sin conversión, sin impuesto, sólo cargo de servicio
    assert result["precio_por_noche"] == 100.0
    assert result["subtotal"] == 100.0
    assert result["impuestos_y_cargos"] == 10.0  # sólo el cargo, IVA = 0
    assert result["total"] == 110.0
    assert result["moneda"] == "USD"


# ── Tests de validación de inputs ─────────────────────────────────────────────


def test_fechas_invalidas_mismo_dia(repo, categoria):
    """check-in == check-out → error."""
    repo.obtain_category_by_id.return_value = categoria
    result = CalculateRoomPrice(repo).execute(
        categoria.id_categoria, date(2026, 10, 14), date(2026, 10, 14), "Colombia"
    )
    assert "error" in result
    assert "Invalid dates" in result["error"]


def test_fechas_invalidas_check_in_posterior(repo, categoria):
    """check-in > check-out → error."""
    repo.obtain_category_by_id.return_value = categoria
    result = CalculateRoomPrice(repo).execute(
        categoria.id_categoria, date(2026, 10, 15), date(2026, 10, 14), "Colombia"
    )
    assert "error" in result


def test_categoria_no_encontrada(repo):
    """Categoría inexistente → error con id_categoria."""
    repo.obtain_category_by_id.return_value = None
    repo.obtain_tax_config_by_country.return_value = None
    fake_id = uuid4()
    result = CalculateRoomPrice(repo).execute(
        fake_id, date(2026, 10, 14), date(2026, 10, 16), "Colombia"
    )
    assert result["error"] == "Category not found"
    assert result["id_categoria"] == str(fake_id)
