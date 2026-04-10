"""
Propósito del archivo: Definición de modelos ORM persistidos en PostgreSQL.
Rol dentro del microservicio: Mapea la estructura de tablas utilizada por AuthService para autenticación y lectura de identidad.
"""

import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id_usuario: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(100), nullable=False)
    partner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)