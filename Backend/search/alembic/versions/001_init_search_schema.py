"""Inicializa el schema de search con tablas hospedajes y destinos.

Revision ID: 001_init_search_schema
Revises: 
Create Date: 2026-05-05 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_init_search_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea el schema search y las tablas hospedajes y destinos."""
    # Crear schema si no existe
    op.execute("CREATE SCHEMA IF NOT EXISTS search")
    
    # Tabla hospedajes
    op.execute("""
        CREATE TABLE IF NOT EXISTS search.hospedajes (
            id_propiedad UUID PRIMARY KEY,
            id_categoria UUID,
            propiedad_nombre TEXT,
            categoria_nombre TEXT,
            imagen_principal_url TEXT,
            amenidades_destacadas JSONB,
            estrellas INTEGER,
            rating_promedio NUMERIC,
            ciudad TEXT,
            estado_provincia TEXT,
            pais TEXT,
            coordenadas JSONB,
            capacidad_pax INTEGER,
            precio_base NUMERIC,
            moneda TEXT,
            es_reembolsable BOOLEAN,
            disponibilidad JSONB
        )
    """)
    
    # Tabla destinos
    op.execute("""
        CREATE TABLE IF NOT EXISTS search.destinos (
            id_destino UUID PRIMARY KEY,
            ciudad TEXT NOT NULL,
            ciudad_lower TEXT NOT NULL,
            estado_provincia TEXT,
            pais TEXT NOT NULL,
            CONSTRAINT unq_destino UNIQUE (ciudad_lower, estado_provincia, pais)
        )
    """)
    
    # Índice para búsquedas por prefijo
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_destinos_ciudad_prefix
        ON search.destinos (ciudad_lower varchar_pattern_ops)
    """)


def downgrade() -> None:
    """Elimina las tablas y el schema."""
    op.execute("DROP INDEX IF EXISTS idx_destinos_ciudad_prefix")
    op.execute("DROP TABLE IF EXISTS search.destinos")
    op.execute("DROP TABLE IF EXISTS search.hospedajes")
    op.execute("DROP SCHEMA IF EXISTS search")
