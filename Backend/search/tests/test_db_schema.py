"""Pruebas unitarias para la creación del esquema SQLite local."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.infrastructure.db_schema import ensure_local_sqlite_database
from app.config import Settings


@pytest.fixture
def mock_settings(monkeypatch, tmp_path):
    """Fixture que configura settings para usar un directorio temporal."""
    settings = Settings(sqlite_path=str(tmp_path / "test_search.db"))
    monkeypatch.setattr("app.infrastructure.db_schema.settings", settings)
    return settings


class TestEnsureLocalSqliteDatabase:
    """Verifica la creación y población de la base SQLite local."""

    def test_crea_archivo_sqlite(self, mock_settings):
        """Debe crear el archivo de base de datos si no existe."""
        ensure_local_sqlite_database()
        assert mock_settings.sqlite_database_path.exists()

    def test_crea_tabla_hospedajes(self, mock_settings):
        """Debe crear la tabla hospedajes con las columnas esperadas."""
        ensure_local_sqlite_database()
        conn = sqlite3.connect(mock_settings.sqlite_database_path)
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='hospedajes'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_crea_tabla_destinos(self, mock_settings):
        """Debe crear la tabla destinos."""
        ensure_local_sqlite_database()
        conn = sqlite3.connect(mock_settings.sqlite_database_path)
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='destinos'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_inserta_datos_seed(self, mock_settings):
        """Si la tabla está vacía, debe insertar datos seed."""
        ensure_local_sqlite_database()
        conn = sqlite3.connect(mock_settings.sqlite_database_path)
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM hospedajes")
            count = cursor.fetchone()[0]
            assert count > 0
        finally:
            conn.close()

    def test_inserta_destinos_seed(self, mock_settings):
        """Si la tabla de destinos está vacía, debe insertar destinos seed."""
        ensure_local_sqlite_database()
        conn = sqlite3.connect(mock_settings.sqlite_database_path)
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM destinos")
            count = cursor.fetchone()[0]
            assert count > 0
        finally:
            conn.close()

    def test_es_idempotente(self, mock_settings):
        """Llamar dos veces no debe duplicar los datos."""
        ensure_local_sqlite_database()
        conn = sqlite3.connect(mock_settings.sqlite_database_path)
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM hospedajes")
            count_primera = cursor.fetchone()[0]
        finally:
            conn.close()

        ensure_local_sqlite_database()
        conn = sqlite3.connect(mock_settings.sqlite_database_path)
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM hospedajes")
            count_segunda = cursor.fetchone()[0]
            assert count_primera == count_segunda
        finally:
            conn.close()

    def test_hospedajes_tiene_columnas_correctas(self, mock_settings):
        """La tabla hospedajes debe tener las columnas esperadas."""
        ensure_local_sqlite_database()
        conn = sqlite3.connect(mock_settings.sqlite_database_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute("SELECT * FROM hospedajes LIMIT 1")
            row = cursor.fetchone()
            columnas = row.keys()
            assert "id_propiedad" in columnas
            assert "id_categoria" in columnas
            assert "propiedad_nombre" in columnas
            assert "ciudad" in columnas
            assert "pais" in columnas
            assert "precio_base" in columnas
        finally:
            conn.close()

    def test_id_categoria_es_primary_key(self, mock_settings):
        """id_categoria debe ser la primary key."""
        ensure_local_sqlite_database()
        conn = sqlite3.connect(mock_settings.sqlite_database_path)
        try:
            cursor = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='hospedajes'"
            )
            ddl = cursor.fetchone()[0]
            assert "PRIMARY KEY" in ddl.upper()
        finally:
            conn.close()

    def test_destinos_tiene_indice(self, mock_settings):
        """La tabla destinos debe tener un índice sobre ciudad_lower."""
        ensure_local_sqlite_database()
        conn = sqlite3.connect(mock_settings.sqlite_database_path)
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='destinos'"
            )
            indices = [row[0] for row in cursor.fetchall()]
            assert any("ciudad" in idx.lower() for idx in indices)
        finally:
            conn.close()
