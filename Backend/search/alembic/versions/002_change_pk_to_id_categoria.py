"""Cambia la PK de hospedajes de id_propiedad a id_categoria.

Revision ID: 002_change_pk_to_id_categoria
Revises: 001_init_search_schema
Create Date: 2026-05-05 10:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_change_pk_to_id_categoria"
down_revision: Union[str, None] = "001_init_search_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cambia la primary key de id_propiedad a id_categoria."""
    # Eliminar constraint PK actual
    op.execute("ALTER TABLE search.hospedajes DROP CONSTRAINT IF EXISTS hospedajes_pkey")
    
    # Hacer id_categoria NOT NULL
    op.execute("ALTER TABLE search.hospedajes ALTER COLUMN id_categoria SET NOT NULL")
    
    # Crear nueva PK en id_categoria
    op.execute("ALTER TABLE search.hospedajes ADD CONSTRAINT hospedajes_pkey PRIMARY KEY (id_categoria)")
    
    # Crear índice en id_propiedad para lookups eficientes
    op.execute("CREATE INDEX IF NOT EXISTS idx_hospedajes_id_propiedad ON search.hospedajes (id_propiedad)")


def downgrade() -> None:
    """Revierte el cambio de PK volviendo a id_propiedad."""
    # Eliminar índice
    op.execute("DROP INDEX IF EXISTS idx_hospedajes_id_propiedad")
    
    # Eliminar constraint PK actual
    op.execute("ALTER TABLE search.hospedajes DROP CONSTRAINT IF EXISTS hospedajes_pkey")
    
    # Permitir NULL en id_categoria nuevamente
    op.execute("ALTER TABLE search.hospedajes ALTER COLUMN id_categoria DROP NOT NULL")
    
    # Restaurar PK en id_propiedad
    op.execute("ALTER TABLE search.hospedajes ADD CONSTRAINT hospedajes_pkey PRIMARY KEY (id_propiedad)")
