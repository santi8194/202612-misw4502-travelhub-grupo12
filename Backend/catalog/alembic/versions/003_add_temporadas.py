"""Crea tabla temporadas para ajustes de precio por fechas.

Revision ID: 003_add_temporadas
Revises: 002_add_tarifas_diferenciadas
Create Date: 2026-04-25
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PgUUID

revision = "003_add_temporadas"
down_revision = "002_add_tarifas_diferenciadas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "temporadas",
        sa.Column("id_temporada", PgUUID(as_uuid=True), primary_key=True),
        sa.Column(
            "id_propiedad",
            PgUUID(as_uuid=True),
            sa.ForeignKey("propiedades.id_propiedad", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("fecha_inicio", sa.String(10), nullable=False),
        sa.Column("fecha_fin", sa.String(10), nullable=False),
        sa.Column("porcentaje", sa.Numeric(5, 2), nullable=False),
    )
    op.create_index("ix_temporadas_id_propiedad", "temporadas", ["id_propiedad"])


def downgrade() -> None:
    op.drop_index("ix_temporadas_id_propiedad", table_name="temporadas")
    op.drop_table("temporadas")
