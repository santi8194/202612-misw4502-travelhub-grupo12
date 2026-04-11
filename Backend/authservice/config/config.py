"""
Configuracion global del auth service.

Todas las variables sensibles deben llegar por entorno o archivo .env.
"""

from urllib.parse import quote_plus

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuracion centralizada del servicio."""

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    PROJECT_NAME: str = "Auth Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/auth"

    # Configuracion principal para la seguridad con JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Politicas para el bloqueo por proteccion contra fuerza bruta
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # Configuracion de la base de datos
    DB_DRIVER: str = "postgresql+psycopg2"
    DB_HOST: str | None = None
    DB_PORT: int = 5432
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DATABASE_URL: str | None = None

    def get_database_url(self) -> str:
        """Obtiene la URL de conexion de SQLAlchemy."""
        if self.DATABASE_URL:
            return self.DATABASE_URL

        required_values = {
            "DB_HOST": self.DB_HOST,
            "DB_NAME": self.DB_NAME,
            "DB_USER": self.DB_USER,
            "DB_PASSWORD": self.DB_PASSWORD,
        }
        missing_values = [key for key, value in required_values.items() if not value]

        if missing_values:
            raise ValueError(
                "Faltan variables de entorno para la base de datos: "
                + ", ".join(missing_values)
            )

        return (
            f"{self.DB_DRIVER}://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
