"""Agrega tabla configuracion_impuestos_pais y fusiona ramas 002.

Revision ID: 003_add_configuracion_impuestos_pais
Revises: 002_add_tarifas_diferenciadas, 002_catalog_uuid_reconcile
Create Date: 2026-04-25
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "003_impuestos_pais"
down_revision = ("002_add_tarifas_diferenciadas", "002_catalog_uuid_reconcile")
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "configuracion_impuestos_pais" not in inspector.get_table_names():
        op.create_table(
            "configuracion_impuestos_pais",
            sa.Column("pais", sa.String(), nullable=False),
            sa.Column("moneda", sa.String(3), nullable=False),
            sa.Column("simbolo_moneda", sa.String(5), nullable=False),
            sa.Column("locale", sa.String(10), nullable=False),
            sa.Column("decimales", sa.Integer(), nullable=False),
            sa.Column("tasa_usd", sa.Numeric(12, 4), nullable=False),
            sa.Column("impuesto_nombre", sa.String(), nullable=False),
            sa.Column("impuesto_tasa", sa.Numeric(5, 4), nullable=False),
            sa.PrimaryKeyConstraint("pais"),
        )


def downgrade() -> None:
    op.drop_table("configuracion_impuestos_pais")
