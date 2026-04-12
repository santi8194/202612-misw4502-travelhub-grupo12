"""
Propósito del archivo: Configuración y administración de conexión a la base de datos.
Rol dentro del microservicio: Provee el engine de SQLAlchemy, la sesión y utilidades para inicializar la BD.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.config import settings

# URL de conexión a PostgreSQL
DATABASE_URL = settings.DATABASE_URL

# Crear el engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica que la conexión esté activa antes de ejecutar queries
    echo=False,  # Cambiar a True para debugging de SQL
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos ORM
Base = declarative_base()


def get_db():
    """
    Dependency injection para obtener una sesión de BD en los endpoints FastAPI.
    Uso: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas definidas en los modelos ORM.
    Esta función se llama típicamente al arrancar la aplicación o antes de pruebas.
    """
    Base.metadata.create_all(bind=engine)
