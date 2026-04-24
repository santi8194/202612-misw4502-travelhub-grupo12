"""Application settings loaded from environment variables."""

from __future__ import annotations

from pathlib import Path

from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration for the search micro-service."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    opensearch_endpoint: str = "https://localhost:9200"
    opensearch_index: str = "hospedajes"
    opensearch_verify_certs: bool = False
    opensearch_user: str | None = None
    opensearch_password: str | None = None
    repository_type: str = "postgres"

    db_host: str | None = None
    db_port: int = 5432
    db_name: str | None = None
    db_user: str | None = None
    db_password: str | None = None
    sqlite_path: str = "data/search.db"

    @property
    def use_postgres_database(self) -> bool:
        """Return True when all Postgres connection settings are available."""
        return all([self.db_host, self.db_name, self.db_user, self.db_password])

    @property
    def sqlite_database_path(self) -> Path:
        """Resolve the absolute path for the local SQLite database."""
        sqlite_path = Path(self.sqlite_path)
        if sqlite_path.is_absolute():
            return sqlite_path
        return Path(__file__).resolve().parents[1] / sqlite_path

    @property
    def database_url(self) -> str:
        """Build the active database connection URL."""
        if self.use_postgres_database:
            return (
                f"postgresql://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )

        sqlite_path = self.sqlite_database_path
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{sqlite_path.as_posix()}"

    @model_validator(mode="after")
    def validate_opensearch_credentials(self) -> "Settings":
        """Require OpenSearch credentials only when that engine is enabled."""
        if self.repository_type == "opensearch":
            missing = [
                key
                for key, value in {
                    "OPENSEARCH_USER": self.opensearch_user,
                    "OPENSEARCH_PASSWORD": self.opensearch_password,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(
                    "Missing required OpenSearch settings: " + ", ".join(missing)
                )
        return self


settings = Settings()
