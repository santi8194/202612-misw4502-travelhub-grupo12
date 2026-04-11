"""Application settings loaded from environment variables."""

from __future__ import annotations

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
    # "opensearch" or "postgres"
    repository_type: str = "postgres"
    postgres_url: str = "postgresql://travelhub:travelhub@localhost:5432/travelhub"

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
