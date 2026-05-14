"""Tests unitarios para event_handlers del microservicio Search."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.infrastructure.event_handlers import (
    _update_postgres_availability,
    _update_postgres_pricing,
    _update_sqlite_availability,
    _update_sqlite_pricing,
    handle_event,
    handle_inventory_updated,
    handle_pricing_updated,
)

_SETTINGS = "app.infrastructure.event_handlers.settings"


# ─── helpers ───

def _make_pg_pool():
    """Crea un mock de asyncpg pool para pruebas de PostgreSQL."""
    conn = AsyncMock()
    conn.execute = AsyncMock(return_value=None)

    acquire_cm = AsyncMock()
    acquire_cm.__aenter__ = AsyncMock(return_value=conn)
    acquire_cm.__aexit__ = AsyncMock(return_value=None)

    pool = MagicMock()
    pool.acquire = MagicMock(return_value=acquire_cm)
    return pool, conn


def _make_sqlite_db(tmp_path, cat_id: UUID, disponibilidad: list | None = None):
    """Crea una base de datos SQLite temporal con un registro de hospedaje."""
    db_path = str(tmp_path / "search.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE hospedajes (id_categoria TEXT, disponibilidad TEXT, precio_base REAL, moneda TEXT)")
    conn.execute(
        "INSERT INTO hospedajes VALUES (?, ?, ?, ?)",
        (str(cat_id), json.dumps(disponibilidad or []), 100.0, "COP"),
    )
    conn.commit()
    conn.close()
    return db_path


# ─── handle_event (router) ───

def test_handle_event_routing_key_desconocida(capsys):
    """Evento con routing_key no reconocida imprime mensaje y no lanza error."""
    handle_event({"type": "unknown"}, "routing.desconocida", pool=None, loop=None)
    assert "no reconocido" in capsys.readouterr().out


def test_handle_event_event_type_desconocido(capsys):
    """Tipo de evento no reconocido imprime mensaje y no lanza error."""
    handle_event({}, "otro.evento", pool=None, loop=None)
    assert "no reconocido" in capsys.readouterr().out


def test_handle_event_enruta_inventory_por_routing_key():
    """handle_event invoca handle_inventory_updated para catalog.inventory.updated."""
    data = {"id_categoria": str(uuid4()), "fecha": "2026-06-01", "cupos_disponibles": 5}
    with patch(
        "app.infrastructure.event_handlers.handle_inventory_updated",
        new_callable=AsyncMock,
    ) as mock_h:
        handle_event(data, "catalog.inventory.updated", pool=None, loop=None)
    mock_h.assert_awaited_once()


def test_handle_event_enruta_pricing_por_routing_key():
    """handle_event invoca handle_pricing_updated para catalog.category.pricing.updated."""
    data = {"id_categoria": str(uuid4()), "tarifa_base_monto": "250.00", "moneda": "COP"}
    with patch(
        "app.infrastructure.event_handlers.handle_pricing_updated",
        new_callable=AsyncMock,
    ) as mock_h:
        handle_event(data, "catalog.category.pricing.updated", pool=None, loop=None)
    mock_h.assert_awaited_once()


def test_handle_event_enruta_por_event_type():
    """handle_event enruta por event_type aunque el routing_key sea diferente."""
    data = {"type": "InventarioActualizado", "id_categoria": str(uuid4()), "fecha": "2026-06-01", "cupos_disponibles": 3}
    with patch(
        "app.infrastructure.event_handlers.handle_inventory_updated",
        new_callable=AsyncMock,
    ) as mock_h:
        handle_event(data, "cualquier.key", pool=None, loop=None)
    mock_h.assert_awaited_once()


# ─── handle_inventory_updated ───

@pytest.mark.asyncio
async def test_handle_inventory_updated_postgres_cupos_positivos():
    """Llama a _update_postgres_availability cuando use_postgres_database=True y cupos > 0."""
    pool, conn = _make_pg_pool()
    data = {"id_categoria": str(uuid4()), "fecha": "2026-06-01", "cupos_disponibles": 3}

    with patch(_SETTINGS) as s:
        s.use_postgres_database = True
        await handle_inventory_updated(data, pool)

    conn.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_inventory_updated_postgres_cupos_cero():
    """Llama a _update_postgres_availability cuando cupos == 0 (eliminar fecha)."""
    pool, conn = _make_pg_pool()
    data = {"id_categoria": str(uuid4()), "fecha": "2026-06-01", "cupos_disponibles": 0}

    with patch(_SETTINGS) as s:
        s.use_postgres_database = True
        await handle_inventory_updated(data, pool)

    conn.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_inventory_updated_campo_faltante_lanza_error():
    """Lanza ValueError cuando falta un campo requerido en el evento."""
    with pytest.raises(ValueError, match="faltante"):
        await handle_inventory_updated({"id_categoria": str(uuid4())}, pool=None)


@pytest.mark.asyncio
async def test_handle_inventory_updated_sqlite(tmp_path):
    """Llama a _update_sqlite_availability cuando use_postgres_database=False."""
    cat_id = uuid4()
    db_path = _make_sqlite_db(tmp_path, cat_id)
    data = {"id_categoria": str(cat_id), "fecha": "2026-07-01", "cupos_disponibles": 4}

    with patch(_SETTINGS) as s:
        s.use_postgres_database = False
        s.sqlite_database_path = db_path
        await handle_inventory_updated(data, pool=None)

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT disponibilidad FROM hospedajes").fetchone()
    conn.close()
    result = json.loads(row[0])
    assert result == [{"fecha": "2026-07-01", "cupos": 4}]


# ─── handle_pricing_updated ───

@pytest.mark.asyncio
async def test_handle_pricing_updated_postgres():
    """Actualiza precio en postgres cuando use_postgres_database=True."""
    pool, conn = _make_pg_pool()
    data = {"id_categoria": str(uuid4()), "tarifa_base_monto": "150.00", "moneda": "USD"}

    with patch(_SETTINGS) as s:
        s.use_postgres_database = True
        await handle_pricing_updated(data, pool)

    conn.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_pricing_updated_sqlite(tmp_path):
    """Actualiza precio en SQLite cuando use_postgres_database=False."""
    cat_id = uuid4()
    db_path = _make_sqlite_db(tmp_path, cat_id)
    data = {"id_categoria": str(cat_id), "tarifa_base_monto": "200.00", "moneda": "USD"}

    with patch(_SETTINGS) as s:
        s.use_postgres_database = False
        s.sqlite_database_path = db_path
        await handle_pricing_updated(data, pool=None)

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT precio_base, moneda FROM hospedajes").fetchone()
    conn.close()
    assert row[0] == 200.0
    assert row[1] == "USD"


@pytest.mark.asyncio
async def test_handle_pricing_updated_campo_faltante_lanza_error():
    """Lanza ValueError cuando falta un campo requerido."""
    with pytest.raises(ValueError, match="faltante"):
        await handle_pricing_updated({"id_categoria": str(uuid4())}, pool=None)


# ─── _update_sqlite_availability ───

@pytest.mark.asyncio
async def test_sqlite_availability_upsert_nueva_fecha(tmp_path):
    """Inserta objeto {fecha, cupos} cuando cupos > 0 y la fecha no existe."""
    cat_id = uuid4()
    db_path = _make_sqlite_db(tmp_path, cat_id, disponibilidad=[])

    with patch(_SETTINGS) as s:
        s.sqlite_database_path = db_path
        await _update_sqlite_availability(cat_id, date(2026, 6, 1), 5)

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT disponibilidad FROM hospedajes").fetchone()
    conn.close()
    assert json.loads(row[0]) == [{"fecha": "2026-06-01", "cupos": 5}]


@pytest.mark.asyncio
async def test_sqlite_availability_reemplaza_fecha_existente(tmp_path):
    """Reemplaza cupos de una fecha que ya existe en el array."""
    cat_id = uuid4()
    existing = [{"fecha": "2026-06-01", "cupos": 10}]
    db_path = _make_sqlite_db(tmp_path, cat_id, disponibilidad=existing)

    with patch(_SETTINGS) as s:
        s.sqlite_database_path = db_path
        await _update_sqlite_availability(cat_id, date(2026, 6, 1), 3)

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT disponibilidad FROM hospedajes").fetchone()
    conn.close()
    result = json.loads(row[0])
    assert result == [{"fecha": "2026-06-01", "cupos": 3}]


@pytest.mark.asyncio
async def test_sqlite_availability_elimina_fecha_cupos_cero(tmp_path):
    """Elimina la fecha del array cuando cupos == 0."""
    cat_id = uuid4()
    existing = [{"fecha": "2026-06-01", "cupos": 5}, {"fecha": "2026-06-02", "cupos": 3}]
    db_path = _make_sqlite_db(tmp_path, cat_id, disponibilidad=existing)

    with patch(_SETTINGS) as s:
        s.sqlite_database_path = db_path
        await _update_sqlite_availability(cat_id, date(2026, 6, 1), 0)

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT disponibilidad FROM hospedajes").fetchone()
    conn.close()
    result = json.loads(row[0])
    assert result == [{"fecha": "2026-06-02", "cupos": 3}]


@pytest.mark.asyncio
async def test_sqlite_availability_categoria_no_encontrada(tmp_path, capsys):
    """No falla y emite mensaje cuando la categoría no existe en la BD."""
    db_path = str(tmp_path / "empty.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE hospedajes (id_categoria TEXT, disponibilidad TEXT)")
    conn.commit()
    conn.close()

    with patch(_SETTINGS) as s:
        s.sqlite_database_path = db_path
        await _update_sqlite_availability(uuid4(), date(2026, 6, 1), 3)

    assert "no encontrada" in capsys.readouterr().out


# ─── _update_sqlite_pricing ───

@pytest.mark.asyncio
async def test_sqlite_pricing_actualiza_precio(tmp_path):
    """Actualiza precio_base y moneda en SQLite correctamente."""
    cat_id = uuid4()
    db_path = _make_sqlite_db(tmp_path, cat_id)

    with patch(_SETTINGS) as s:
        s.sqlite_database_path = db_path
        await _update_sqlite_pricing(cat_id, 350.0, "EUR")

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT precio_base, moneda FROM hospedajes").fetchone()
    conn.close()
    assert row[0] == 350.0
    assert row[1] == "EUR"
