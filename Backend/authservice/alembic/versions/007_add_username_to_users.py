"""Add username column to users table

Revision ID: 007_add_username_to_users
Revises: 006_create_user_sessions
Create Date: 2026-04-23 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "007_add_username_to_users"
down_revision = "006_create_user_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("username", sa.String(255), nullable=True),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # Poblar username de Cognito para usuarios existentes
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE users SET username = :username WHERE email = :email"),
        {"username": "e468d448-9051-7099-89d5-5740f302b523", "email": "admin@hotel1.com"},
    )


def downgrade() -> None:
    op.drop_index("ix_users_username", table_name="users")
    op.drop_column("users", "username")
