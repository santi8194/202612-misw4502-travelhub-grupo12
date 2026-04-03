"""Add seed data: roles and admin user

Revision ID: 002_seed_roles_and_admin
Revises: 001_initial_schema
Create Date: 2025-04-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision = '002_seed_roles_and_admin'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None

# Configurar el contexto de hash compatible con la aplicación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def upgrade() -> None:
    """Insertar roles y usuario administrador inicial"""
    
    # Conectar a la tabla para inserciones
    connection = op.get_bind()
    
    # Crear UUIDs consistentes para roles
    admin_role_id = str(uuid.UUID("550e8400-e29b-41d4-a716-446655440000"))
    user_role_id = str(uuid.UUID("770e8400-e29b-41d4-a716-446655440000"))
    admin_user_id = str(uuid.UUID("550e8400-e29b-41d4-a716-446655440000"))
    

    now = datetime.utcnow()
    
    # Insertar roles
    roles_insert = sa.text("""
    INSERT INTO roles (id, name, description, created_at)
    VALUES (:id, :name, :description, :created_at)
    """)

    connection.execute(
        roles_insert,
        [
            {
                "id": admin_role_id,
                "name": "ADMIN_HOTEL",
                "description": "Hotel administrator with full access",
                "created_at": now
            },
            {
                "id": user_role_id,
                "name": "USER",
                "description": "Regular user with basic access",
                "created_at": now
            }
        ]
    )
    
    # Insertar usuario administrador
    admin_email = "admin@travelhub.com"
    admin_password_hash = get_password_hash("123456")
    
    user_insert = sa.text("""
    INSERT INTO users (id, email, full_name, password_hash, is_active, created_at, updated_at)
    VALUES (:id, :email, :full_name, :password_hash, :is_active, :created_at, :updated_at)
    """)

    connection.execute(
        user_insert,
        {
            "id": admin_user_id,
            "email": admin_email,
            "full_name": "Admin User",
            "password_hash": admin_password_hash,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
    )
    
    # Asignar role ADMIN_HOTEL al usuario administrador
    assign_role = sa.text("""
    INSERT INTO user_roles (user_id, role_id)
    VALUES (:user_id, :role_id)
    """)

    connection.execute(
        assign_role,
        {
            "user_id": admin_user_id,
            "role_id": admin_role_id
        }
    )
    
    connection.commit()


def downgrade() -> None:
    """Eliminar datos de seed"""
    connection = op.get_bind()
    
    admin_user_id = "550e8400-e29b-41d4-a716-446655440000"
    admin_role_id = "660e8400-e29b-41d4-a716-446655440000"
    user_role_id  = "770e8400-e29b-41d4-a716-446655440000"
    
    # Eliminar relaciones de usuario-rol
    connection.execute(
        sa.text(f"DELETE FROM user_roles WHERE user_id = '{admin_user_id}'")
    )
    
    # Eliminar usuario admin
    connection.execute(
        sa.text(f"DELETE FROM users WHERE id = '{admin_user_id}'")
    )
    
    # Eliminar roles
    connection.execute(
        sa.text(f"DELETE FROM roles WHERE id IN ('{admin_role_id}', '{user_role_id}')")
    )
    
    connection.commit()
