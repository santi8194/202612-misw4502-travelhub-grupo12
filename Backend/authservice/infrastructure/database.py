"""
Propósito del archivo: Configuración de conexión y sesión con PostgreSQL.
Rol dentro del microservicio: Centraliza el engine de SQLAlchemy, la creación de tablas y la carga inicial mínima de usuarios de prueba.
"""

import uuid
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from config.config import settings
from config.security import get_password_hash


class Base(DeclarativeBase):
    pass


_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(settings.get_database_url(), pool_pre_ping=True)
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
    return _session_factory


def new_session() -> Session:
    return get_session_factory()()


def init_db() -> None:
    from infrastructure.models import UserModel

    Base.metadata.create_all(bind=get_engine())

    with new_session() as session:
        existing_user = session.execute(select(UserModel.id_usuario).limit(1)).scalar_one_or_none()
        if existing_user is not None:
            return

        default_users = [
            UserModel(
                id_usuario=uuid.uuid4(),
                email="admin@hotel.com",
                password_hash=get_password_hash("123456"),
                rol="ADMIN_HOTEL",
                partner_id=uuid.uuid4(),
            ),
            UserModel(
                id_usuario=uuid.uuid4(),
                email="user@hotel.com",
                password_hash=get_password_hash("user123"),
                rol="USER",
                partner_id=None,
            ),
        ]

        session.add_all(default_users)
        session.commit()