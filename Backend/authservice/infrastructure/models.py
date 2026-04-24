"""
Propósito del archivo: Define los modelos ORM (SQLAlchemy) para usuarios, roles y su relación.
Rol dentro del microservicio: Representa la estructura de datos persistente en PostgreSQL.
"""

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Table, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from infrastructure.database import Base


# Tabla de asociación many-to-many entre usuarios y roles
user_roles_association = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
)


class Role(Base):
    """
    Modelo para roles (ADMIN_HOTEL, USER, etc.).
    Permite un sistema flexible de permisos basado en roles.
    """
    __tablename__ = 'roles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relación hacia usuarios
    users = relationship(
        'User',
        secondary=user_roles_association,
        back_populates='roles',
        cascade='all, delete'
    )
    
    def __repr__(self):
        return f"<Role {self.name}>"


class User(Base):
    """
    Modelo para usuarios del sistema.
    Almacena credenciales, información de contacto y roles asignados.
    """
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=True, index=True)
    full_name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    partner_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    is_active = Column(String(10), default='true', nullable=False)  # 'true' o 'false' para compatibilidad
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relación hacia roles
    roles = relationship(
        'Role',
        secondary=user_roles_association,
        back_populates='users',
        cascade='all, delete'
    )
    sessions = relationship('UserSession', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User {self.email}>"


class UserSession(Base):
    """
    Modelo de sesión persistida para soportar expiración por inactividad y refresh tokens rotativos.
    """
    __tablename__ = 'user_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    refresh_token_hash = Column(String(64), nullable=False, unique=True, index=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship('User', back_populates='sessions')

    def __repr__(self):
        return f"<UserSession {self.id}>"
