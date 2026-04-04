"""
Propósito del archivo: Definición de variables de configuración general.
Rol dentro del microservicio: Provee todas las constantes globales y variables de entorno requeridas, como la llave secreta, el algoritmo JWT y políticas de bloqueo.
"""

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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_IDLE_TIMEOUT_MINUTES: int = 5
    
    # Políticas para el bloqueo por protección contra fuerza bruta
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # Configuración de base de datos
    DB_USER: str = "auth_user"
    DB_PASSWORD: str = "auth_password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "auth_db"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construye la URL de conexión a PostgreSQL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        case_sensitive = True
        env_file = ".env"


# Instancia singleton para ser importada en el resto de la aplicación
settings = Settings()
