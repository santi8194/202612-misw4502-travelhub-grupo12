"""Restaura la revision historica 003_impuestos_pais.

Revision ID: 003_impuestos_pais
Revises: 002_catalog_uuid_reconcile, 002_add_tarifas_diferenciadas
Create Date: 2026-04-26
"""

from __future__ import annotations


revision = "003_impuestos_pais"
down_revision = ("002_catalog_uuid_reconcile", "002_add_tarifas_diferenciadas")
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op.

    La base RDS de desarrollo ya referencia esta revision en alembic_version.
    El modelo actual ya incluye porcentaje_impuesto en propiedades, por lo que
    esta migracion solo restaura el identificador historico para que Alembic
    pueda resolver el grafo de migraciones.
    """


def downgrade() -> None:
    """No-op para evitar perdida de datos en entornos compartidos."""
