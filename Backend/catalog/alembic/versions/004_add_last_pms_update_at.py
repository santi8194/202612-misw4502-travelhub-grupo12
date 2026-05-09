"""add last_pms_update_at to inventario

Revision ID: 004
Revises: 003
Create Date: 2026-05-09

"""
from alembic import op
import sqlalchemy as sa


revision = '004'
down_revision = '003_add_configuracion_impuestos_pais'
branch_labels = None
depends_on = None


def upgrade():
    """Agrega campo last_pms_update_at para idempotencia de eventos PMS."""
    op.add_column(
        'inventario',
        sa.Column('last_pms_update_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    op.execute("""
        COMMENT ON COLUMN inventario.last_pms_update_at IS 
        'Timestamp del último evento PMS procesado. Usado para idempotencia:
         si llega un evento con timestamp más viejo, se descarta.'
    """)


def downgrade():
    """Elimina el campo last_pms_update_at."""
    op.drop_column('inventario', 'last_pms_update_at')
