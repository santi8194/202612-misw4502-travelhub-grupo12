"""
Proposito del archivo: Configuracion y administracion de conexion a la base de datos.
Rol dentro del microservicio: Provee el engine de SQLAlchemy, la sesion y utilidades para inicializar la BD.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.config import settings

DATABASE_URL = settings.DATABASE_URL
IS_SQLITE = settings.USE_SQLITE

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=not IS_SQLITE,
    echo=False,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Dependency injection para obtener una sesion de BD en los endpoints FastAPI.
    Uso: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _seed_sqlite_defaults() -> None:
    """Carga usuarios y roles base cuando authservice corre con SQLite local."""
    from infrastructure.models import Role, User

    now = datetime.utcnow()
    admin_password_hash = "$2b$12$m9P0Rr8qbPoz7Xl6vlBH5uxXUzEkT5csbECvp4QmJby3VZI4wBB7e"
    seed_roles = [
        Role(
            id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            name="ADMIN_HOTEL",
            description="Hotel administrator with full access",
            created_at=now,
        ),
        Role(
            id=UUID("770e8400-e29b-41d4-a716-446655440000"),
            name="USER",
            description="Regular user with basic access",
            created_at=now,
        ),
    ]
    seed_users = [
        User(
            id=UUID("990e8400-e29b-41d4-a716-446655440000"),
            email="admin@travelhub.com",
            full_name="Admin User",
            password_hash=admin_password_hash,
            is_active="true",
            created_at=now,
            updated_at=now,
        ),
        User(
            id=UUID("a90e8400-e29b-41d4-a716-446655440000"),
            email="admin@hotel1.com",
            full_name="Admin Hotel 1",
            password_hash=admin_password_hash,
            partner_id=UUID("cc0e8400-e29b-41d4-a716-446655440001"),
            is_active="true",
            created_at=now,
            updated_at=now,
        ),
        User(
            id=UUID("b90e8400-e29b-41d4-a716-446655440000"),
            email="admin@hotel2.com",
            full_name="Admin Hotel 2",
            password_hash=admin_password_hash,
            partner_id=UUID("cc0e8400-e29b-41d4-a716-446655440002"),
            is_active="true",
            created_at=now,
            updated_at=now,
        ),
    ]

    db = SessionLocal()
    try:
        existing_roles = {role.name: role for role in db.query(Role).all()}
        for role in seed_roles:
            if role.name not in existing_roles:
                db.add(role)
                existing_roles[role.name] = role
        db.flush()

        existing_users = {user.email: user for user in db.query(User).all()}
        admin_role = existing_roles["ADMIN_HOTEL"]

        for seed_user in seed_users:
            user = existing_users.get(seed_user.email)
            if user is None:
                user = seed_user
                db.add(user)
                existing_users[user.email] = user
            if admin_role not in user.roles:
                user.roles.append(admin_role)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas definidas en los modelos ORM.
    Esta funcion se llama tipicamente al arrancar la aplicacion o antes de pruebas.
    """
    Base.metadata.create_all(bind=engine)
    if IS_SQLITE:
        _seed_sqlite_defaults()
