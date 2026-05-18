"""Expand reserva estado length for cancellation workflow."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "004_expand_reserva_estado_length"
down_revision = "003_reservas_add_usuario_email"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "reservas",
        "estado",
        existing_type=sa.String(length=20),
        type_=sa.String(length=30),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "reservas",
        "estado",
        existing_type=sa.String(length=30),
        type_=sa.String(length=20),
        existing_nullable=False,
    )
