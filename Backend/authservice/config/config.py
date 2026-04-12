"""
Propósito del archivo: Definición de variables de configuración general.
Rol dentro del microservicio: Provee todas las constantes globales y variables de entorno requeridas,
incluyendo la configuración de AWS Cognito y la conexión a base de datos.
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

    # Configuración de AWS Cognito
    # NOTA: En producción/Kubernetes, estos valores deben ser definidos por variables de entorno (Secrets/ConfigMaps).
    COGNITO_REGION: str = "us-east-1"
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""
    COGNITO_CLIENT_SECRET: str = ""

    @property
    def COGNITO_JWK_URL(self) -> str:
        """URL pública de las claves JWK del User Pool de Cognito."""
        return f"https://cognito-idp.{self.COGNITO_REGION}.amazonaws.com/{self.COGNITO_USER_POOL_ID}/.well-known/jwks.json"

    @property
    def COGNITO_ISSUER(self) -> str:
        """Issuer (emisor) esperado en los tokens JWT de Cognito."""
        return f"https://cognito-idp.{self.COGNITO_REGION}.amazonaws.com/{self.COGNITO_USER_POOL_ID}"

    # Configuración de base de datos
    # NOTA: En producción/Kubernetes, estos valores deben ser definidos por variables de entorno (por ejemplo, desde Secrets o ConfigMaps).
    # Los valores por defecto solo se usan para desarrollo local o si no se encuentra la variable de entorno correspondiente.
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
        extra = "ignore"


# Instancia singleton para ser importada en el resto de la aplicación
settings = Settings()
