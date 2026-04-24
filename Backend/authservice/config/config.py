"""
Proposito del archivo: Definicion de variables de configuracion general.
Rol dentro del microservicio: Provee todas las constantes globales y variables de entorno requeridas,
incluyendo la configuracion de AWS Cognito y la conexion a base de datos.
"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Clase de configuracion que maneja las variables globales.
    Usa BaseSettings para poder ser inicializada a traves de un archivo .env si se requiere.
    """

    PROJECT_NAME: str = "Auth Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/auth"

    COGNITO_REGION: str = "us-east-1"
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""
    COGNITO_CLIENT_SECRET: str = ""

    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int = 5432
    DB_NAME: str | None = None
    SQLITE_PATH: str = "data/auth.db"

    @property
    def COGNITO_JWK_URL(self) -> str:
        """URL publica de las claves JWK del User Pool de Cognito."""
        return f"https://cognito-idp.{self.COGNITO_REGION}.amazonaws.com/{self.COGNITO_USER_POOL_ID}/.well-known/jwks.json"

    @property
    def COGNITO_ISSUER(self) -> str:
        """Issuer esperado en los tokens JWT de Cognito."""
        return f"https://cognito-idp.{self.COGNITO_REGION}.amazonaws.com/{self.COGNITO_USER_POOL_ID}"

    @property
    def USE_SQLITE(self) -> bool:
        """Usa SQLite cuando no se configuraron todas las variables de Postgres."""
        return not all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME])

    @property
    def SQLITE_DATABASE_PATH(self) -> Path:
        """Retorna la ruta absoluta del archivo SQLite local."""
        sqlite_path = Path(self.SQLITE_PATH)
        if sqlite_path.is_absolute():
            return sqlite_path
        return Path(__file__).resolve().parents[1] / sqlite_path

    @property
    def DATABASE_URL(self) -> str:
        """Construye la URL de conexion activa."""
        if self.USE_SQLITE:
            sqlite_path = self.SQLITE_DATABASE_PATH
            sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{sqlite_path.as_posix()}"

        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"


settings = Settings()
