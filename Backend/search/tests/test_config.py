"""Pruebas unitarias para la configuración de la aplicación."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.config import Settings


class TestUsePostgresDatabase:
    """Verifica la propiedad use_postgres_database."""

    def test_retorna_true_cuando_todos_los_campos_estan_presentes(self):
        """Debe retornar True cuando db_host, db_name, db_user y db_password están definidos."""
        settings = Settings(
            db_host="localhost",
            db_name="search",
            db_user="user",
            db_password="pass",
        )
        assert settings.use_postgres_database is True

    def test_retorna_false_cuando_falta_algun_campo(self):
        """Debe retornar False si falta cualquiera de los campos requeridos."""
        settings = Settings(
            db_host="localhost",
            db_name="search",
            db_user="user",
        )
        assert settings.use_postgres_database is False

    def test_retorna_false_cuando_todos_los_campos_faltan(self):
        """Debe retornar False cuando no se define ningún campo de Postgres."""
        settings = Settings()
        assert settings.use_postgres_database is False


class TestSqliteDatabasePath:
    """Verifica la resolución del path de SQLite."""

    def test_path_relativo_se_resuelve(self):
        """Un path relativo debe resolverse contra el directorio padre de config.py."""
        settings = Settings(sqlite_path="data/test.db")
        path = settings.sqlite_database_path
        assert path.is_absolute()
        assert path.name == "test.db"

    def test_path_absoluto_se_mantiene(self):
        """Un path absoluto debe mantenerse sin modificación."""
        settings = Settings(sqlite_path="/tmp/test.db")
        path = settings.sqlite_database_path
        assert str(path) == "/tmp/test.db"


class TestDatabaseUrl:
    """Verifica la construcción de la URL de conexión."""

    def test_url_postgres(self):
        """Cuando Postgres está configurado, debe retornar una URL postgresql://."""
        settings = Settings(
            db_host="db.example.com",
            db_port=5432,
            db_name="search_db",
            db_user="admin",
            db_password="secret123",
        )
        url = settings.database_url
        assert url.startswith("postgresql://")
        assert "admin:secret123" in url
        assert "db.example.com:5432/search_db" in url

    def test_url_sqlite_cuando_no_hay_postgres(self):
        """Sin configuración Postgres, debe retornar una URL sqlite:///."""
        settings = Settings(sqlite_path="data/search.db")
        url = settings.database_url
        assert url.startswith("sqlite:///")


class TestValidateOpensearchCredentials:
    """Verifica la validación de credenciales de OpenSearch."""

    def test_no_lanza_error_cuando_repo_no_es_opensearch(self):
        """No debe validar credenciales si repository_type no es 'opensearch'."""
        settings = Settings(repository_type="postgres")
        assert settings.repository_type == "postgres"

    def test_lanza_error_si_faltan_credenciales(self):
        """Debe lanzar ValueError si faltan OPENSEARCH_USER u OPENSEARCH_PASSWORD."""
        with pytest.raises(ValueError, match="Missing required OpenSearch settings"):
            Settings(
                repository_type="opensearch",
                opensearch_user=None,
                opensearch_password=None,
            )

    def test_no_lanza_error_cuando_credenciales_estan_presentes(self):
        """No debe lanzar error cuando las credenciales están configuradas."""
        settings = Settings(
            repository_type="opensearch",
            opensearch_user="admin",
            opensearch_password="secret",
        )
        assert settings.opensearch_user == "admin"
        assert settings.opensearch_password == "secret"


class TestDefaultValues:
    """Verifica los valores por defecto de Settings."""

    def test_valores_por_defecto(self):
        """Los valores por defecto deben estar correctamente establecidos."""
        settings = Settings()
        assert settings.opensearch_endpoint == "https://localhost:9200"
        assert settings.opensearch_index == "hospedajes"
        assert settings.opensearch_verify_certs is False
        assert settings.repository_type == "postgres"
        assert settings.db_port == 5432
        assert settings.sqlite_path == "data/search.db"
