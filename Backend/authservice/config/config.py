"""
Propósito del archivo: Definición de variables de configuración general.
Rol dentro del microservicio: Provee todas las constantes globales y variables de entorno requeridas, como la llave secreta, el algoritmo JWT y políticas de bloqueo.
"""

from urllib.parse import quote_plus
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Clase de configuración que maneja las variables globales.
    Usa BaseSettings para poder ser inicializada a través de un archivo .env si se requiere.
    """
    PROJECT_NAME: str = "Auth Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/auth"
    
    # Configuración principal para la seguridad con JWT
    SECRET_KEY: str = "super_secret_key_change_in_production_12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Políticas para el bloqueo por protección contra fuerza bruta
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # Configuración de la base de datos
    DB_DRIVER: str = "postgresql+psycopg2"
    DB_HOST: str | None = None
    DB_PORT: int = 5432
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DATABASE_URL: str | None = None

    def get_database_url(self) -> str:
        """
        Obtiene la URL de conexión de SQLAlchemy.
        Prioriza DATABASE_URL completa y, si no existe, la construye a partir de variables separadas.
        """
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

    class Config:
        case_sensitive = True
        env_file = ".env"


# Instancia singleton para ser importada en el resto de la aplicación
settings = Settings()
