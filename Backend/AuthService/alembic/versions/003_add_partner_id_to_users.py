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
    """Agregar columna partner_id nullable en users e índice para búsquedas."""
    op.add_column(
        'users',
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_users_partner_id', 'users', ['partner_id'])


def downgrade() -> None:
    """Revertir columna partner_id e índice asociado."""
    op.drop_index('ix_users_partner_id', table_name='users')
    op.drop_column('users', 'partner_id')
