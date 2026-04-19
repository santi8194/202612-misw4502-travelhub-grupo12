"""Seed extra hotel admin users

Revision ID: 004_seed_hotel_admin_users
Revises: 003_add_partner_id_to_users
Create Date: 2026-04-04 00:00:00.000000

"""

from datetime import datetime
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "004_seed_hotel_admin_users"
down_revision = "003_add_partner_id_to_users"
branch_labels = None
depends_on = None

# Pre-computed bcrypt hash for seed password "123456"
# Generated with: CryptContext(schemes=["bcrypt"]).hash("123456")
ADMIN_PASSWORD_HASH = "$2b$12$m9P0Rr8qbPoz7Xl6vlBH5uxXUzEkT5csbECvp4QmJby3VZI4wBB7e"


def upgrade() -> None:
    connection = op.get_bind()

    admin_role_id = str(uuid.UUID("550e8400-e29b-41d4-a716-446655440000"))
    admin_hotel1_user_id = str(uuid.UUID("a90e8400-e29b-41d4-a716-446655440000"))
    admin_hotel2_user_id = str(uuid.UUID("b90e8400-e29b-41d4-a716-446655440000"))

    # partner_id fijos y deterministas (mismos que en migración 002)
    partner_id_hotel1 = str(uuid.UUID("cc0e8400-e29b-41d4-a716-446655440001"))
    partner_id_hotel2 = str(uuid.UUID("cc0e8400-e29b-41d4-a716-446655440002"))

    now = datetime.utcnow()
    admin_password_hash = ADMIN_PASSWORD_HASH

    user_insert = sa.text("""
    INSERT INTO users (id, email, full_name, password_hash, is_active, partner_id, created_at, updated_at)
    VALUES (:id, :email, :full_name, :password_hash, :is_active, :partner_id, :created_at, :updated_at)
    ON CONFLICT (email) DO NOTHING
    """)

    connection.execute(
        user_insert,
        [
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
    SELECT u.id, :role_id
    FROM users u
    WHERE u.email = :email
    ON CONFLICT (user_id, role_id) DO NOTHING
    """)

    connection.execute(assign_role, {"email": "admin@hotel1.com", "role_id": admin_role_id})
    connection.execute(assign_role, {"email": "admin@hotel2.com", "role_id": admin_role_id})


def downgrade() -> None:
    connection = op.get_bind()

    user_ids = [
        str(uuid.UUID("a90e8400-e29b-41d4-a716-446655440000")),
        str(uuid.UUID("b90e8400-e29b-41d4-a716-446655440000")),
    ]

    connection.execute(
        sa.text("DELETE FROM user_roles WHERE user_id = ANY(:user_ids)"),
        {"user_ids": user_ids},
    )

    connection.execute(
        sa.text("DELETE FROM users WHERE id = ANY(:user_ids)"),
        {"user_ids": user_ids},
    )
