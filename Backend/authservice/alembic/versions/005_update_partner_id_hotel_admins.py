"""Update partner_id for existing hotel admin users

Revision ID: 005_update_partner_id_hotel_admins
Revises: 004_seed_hotel_admin_users
Create Date: 2026-04-04 00:00:00.000000

"""

import uuid

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "005_update_partner_id"
down_revision = "004_seed_hotel_admin_users"
branch_labels = None
depends_on = None

# UUIDs fijos y deterministas (mismos que en migraciones 002 y 004)
PARTNER_ID_HOTEL1 = str(uuid.UUID("cc0e8400-e29b-41d4-a716-446655440001"))
PARTNER_ID_HOTEL2 = str(uuid.UUID("cc0e8400-e29b-41d4-a716-446655440002"))


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text("""
        UPDATE users
        SET partner_id = :partner_id
        WHERE email = :email
          AND (partner_id IS NULL OR partner_id != :partner_id)
        """),
        {"email": "admin@hotel1.com", "partner_id": PARTNER_ID_HOTEL1},
    )

    connection.execute(
        sa.text("""
        UPDATE users
        SET partner_id = :partner_id
        WHERE email = :email
          AND (partner_id IS NULL OR partner_id != :partner_id)
        """),
        {"email": "admin@hotel2.com", "partner_id": PARTNER_ID_HOTEL2},
    )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text("UPDATE users SET partner_id = NULL WHERE email IN ('admin@hotel1.com', 'admin@hotel2.com')"),
    )
