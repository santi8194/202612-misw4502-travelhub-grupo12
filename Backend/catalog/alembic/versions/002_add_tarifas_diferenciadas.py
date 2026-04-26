"""Agrega columnas de tarifas diferenciadas a categorias_habitacion.

Revision ID: 002_add_tarifas_diferenciadas
Revises: 001_initial_schema
Create Date: 2026-04-22
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = "002_add_tarifas_diferenciadas"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("categorias_habitacion", sa.Column("tarifa_fin_de_semana_monto", sa.Numeric(12, 2), nullable=True))
    op.add_column("categorias_habitacion", sa.Column("tarifa_fin_de_semana_moneda", sa.String(3), nullable=True))
    op.add_column("categorias_habitacion", sa.Column("tarifa_fin_de_semana_cargo_servicio", sa.Numeric(12, 2), nullable=True))
    op.add_column("categorias_habitacion", sa.Column("tarifa_temporada_alta_monto", sa.Numeric(12, 2), nullable=True))
    op.add_column("categorias_habitacion", sa.Column("tarifa_temporada_alta_moneda", sa.String(3), nullable=True))
    op.add_column("categorias_habitacion", sa.Column("tarifa_temporada_alta_cargo_servicio", sa.Numeric(12, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("categorias_habitacion", "tarifa_temporada_alta_cargo_servicio")
    op.drop_column("categorias_habitacion", "tarifa_temporada_alta_moneda")
    op.drop_column("categorias_habitacion", "tarifa_temporada_alta_monto")
    op.drop_column("categorias_habitacion", "tarifa_fin_de_semana_cargo_servicio")
    op.drop_column("categorias_habitacion", "tarifa_fin_de_semana_moneda")
    op.drop_column("categorias_habitacion", "tarifa_fin_de_semana_monto")
