"""add sync cursor table

Revision ID: 002
Revises: 001
Create Date: 2026-05-09

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


revision = '002'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """Crea la tabla sync_cursors para tracking de polling."""
    op.create_table(
        'sync_cursors',
        sa.Column('provider_name', sa.String(), nullable=False),
        sa.Column('last_sync_timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('provider_name')
    )

    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("""
            COMMENT ON TABLE sync_cursors IS
            'Cursor de sincronización para polling de inventario PMS'
        """)
        op.execute("""
            COMMENT ON COLUMN sync_cursors.last_sync_timestamp IS
            'Timestamp del último cambio procesado desde el PMS'
        """)


def downgrade():
    """Elimina la tabla sync_cursors."""
    op.drop_table('sync_cursors')
