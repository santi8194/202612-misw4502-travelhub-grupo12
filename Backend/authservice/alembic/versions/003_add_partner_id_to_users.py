"""Add partner_id column to users

Revision ID: 003_add_partner_id_to_users
Revises: 002_seed_roles_and_admin
Create Date: 2026-04-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_partner_id_to_users'
down_revision = '002_seed_roles_and_admin'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Agregar partner_id si no existe (idempotente: BD existentes sin la columna)."""
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS partner_id UUID;
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_users_partner_id ON users (partner_id);
    """)


def downgrade() -> None:
    """Revertir columna partner_id e índice asociado."""
    op.execute("DROP INDEX IF EXISTS ix_users_partner_id;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS partner_id;")
    op.drop_column('users', 'partner_id')
