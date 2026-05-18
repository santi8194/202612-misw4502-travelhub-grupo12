"""Add usuario_email column to reservas.

Revision ID: 003_reservas_add_usuario_email
Revises: 002_cancellation_audit
Create Date: 2026-05-17
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "003_reservas_add_usuario_email"
down_revision = "002_cancellation_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("reservas", sa.Column("usuario_email", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("reservas", "usuario_email")
