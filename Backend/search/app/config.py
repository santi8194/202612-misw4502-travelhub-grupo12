"""Application settings loaded from environment variables."""

from __future__ import annotations

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration for the search micro-service.

    Values are read from environment variables (case-insensitive).
    """

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    opensearch_endpoint: str = "https://localhost:9200"
    opensearch_index: str = "hospedajes"
    opensearch_verify_certs: bool = False
    opensearch_user: str = "admin"
    opensearch_password: str = "MyStr0ng!Pass#2026"
    # "opensearch", "postgres", or "memory"
    repository_type: str = "postgres"
    postgres_url: str = "postgresql://travelhub:travelhub@localhost:5432/travelhub"

settings = Settings()
