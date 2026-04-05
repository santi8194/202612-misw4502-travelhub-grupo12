"""Add seed data: roles and admin user

Revision ID: 002_seed_roles_and_admin
Revises: 001_initial_schema
Create Date: 2025-04-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
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
    """Insertar roles y usuarios administradores iniciales"""

    connection = op.get_bind()

    admin_role_id = str(uuid.UUID("550e8400-e29b-41d4-a716-446655440000"))
    user_role_id = str(uuid.UUID("770e8400-e29b-41d4-a716-446655440000"))
    admin_user_id = str(uuid.UUID("990e8400-e29b-41d4-a716-446655440000"))
    admin_hotel1_user_id = str(uuid.UUID("a90e8400-e29b-41d4-a716-446655440000"))
    admin_hotel2_user_id = str(uuid.UUID("b90e8400-e29b-41d4-a716-446655440000"))

    # partner_id fijos y deterministas por usuario (simulan entidades en PartnerManagement)
    partner_id_hotel1 = str(uuid.UUID("cc0e8400-e29b-41d4-a716-446655440001"))
    partner_id_hotel2 = str(uuid.UUID("cc0e8400-e29b-41d4-a716-446655440002"))

    now = datetime.utcnow()

    roles_insert = sa.text("""
    INSERT INTO roles (id, name, description, created_at)
    VALUES (:id, :name, :description, :created_at)
    ON CONFLICT (id) DO NOTHING
    """)

    connection.execute(
        roles_insert,
        [
            {
                "id": admin_role_id,
                "name": "ADMIN_HOTEL",
                "description": "Hotel administrator with full access",
                "created_at": now,
            },
            {
                "id": user_role_id,
                "name": "USER",
                "description": "Regular user with basic access",
                "created_at": now,
            },
        ],
    )

    admin_password_hash = get_password_hash("123456")

    user_insert = sa.text("""
    INSERT INTO users (id, email, full_name, password_hash, is_active, partner_id, created_at, updated_at)
    VALUES (:id, :email, :full_name, :password_hash, :is_active, :partner_id, :created_at, :updated_at)
    ON CONFLICT (id) DO NOTHING
    """)

    connection.execute(
        user_insert,
        [
            {
                "id": admin_user_id,
                "email": "admin@travelhub.com",
                "full_name": "Admin User",
                "password_hash": admin_password_hash,
                "is_active": True,
                "partner_id": None,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": admin_hotel1_user_id,
                "email": "admin@hotel1.com",
                "full_name": "Admin Hotel 1",
                "password_hash": admin_password_hash,
                "is_active": True,
                "partner_id": partner_id_hotel1,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": admin_hotel2_user_id,
                "email": "admin@hotel2.com",
                "full_name": "Admin Hotel 2",
                "password_hash": admin_password_hash,
                "is_active": True,
                "partner_id": partner_id_hotel2,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )

    assign_role = sa.text("""
    INSERT INTO user_roles (user_id, role_id)
    VALUES (:user_id, :role_id)
    ON CONFLICT (user_id, role_id) DO NOTHING
    """)

    connection.execute(
        assign_role,
        [
            {"user_id": admin_user_id, "role_id": admin_role_id},
            {"user_id": admin_hotel1_user_id, "role_id": admin_role_id},
            {"user_id": admin_hotel2_user_id, "role_id": admin_role_id},
        ],
    )
    
def downgrade() -> None:
    """Eliminar datos de seed"""
    connection = op.get_bind()

    admin_user_id = "990e8400-e29b-41d4-a716-446655440000"
    admin_hotel1_user_id = "a90e8400-e29b-41d4-a716-446655440000"
    admin_hotel2_user_id = "b90e8400-e29b-41d4-a716-446655440000"
    admin_role_id = "550e8400-e29b-41d4-a716-446655440000"
    user_role_id = "770e8400-e29b-41d4-a716-446655440000"

    user_ids = [admin_user_id, admin_hotel1_user_id, admin_hotel2_user_id]

    connection.execute(
        sa.text("DELETE FROM user_roles WHERE user_id = ANY(:user_ids)"),
        {"user_ids": user_ids},
    )

    connection.execute(
        sa.text("DELETE FROM users WHERE id = ANY(:user_ids)"),
        {"user_ids": user_ids},
    )

    connection.execute(
        sa.text("DELETE FROM roles WHERE id IN (:admin_role_id, :user_role_id)"),
        {"admin_role_id": admin_role_id, "user_role_id": user_role_id},
    )
    
