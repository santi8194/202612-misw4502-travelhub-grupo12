"""Fix username for admin@hotel1.com

Revision ID: 008_fix_admin_hotel1_username
Revises: 007_add_username_to_users
Create Date: 2026-04-30 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "008_fix_admin_hotel1_username"
down_revision = "007_add_username_to_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE users SET username = :username WHERE email = :email"),
        {
            "username": "e468d448-9051-7099-89d5-5740f302b523",
            "email": "admin@hotel1.com",
        },
    )


def downgrade() -> None:
    # Irreversible data fix migration.
    pass
