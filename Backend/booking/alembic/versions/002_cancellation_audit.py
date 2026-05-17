"""Add cancellation audit table."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "002_cancellation_audit"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auditoria_cancelacion_reserva",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("id_reserva", sa.String(length=40), nullable=False),
        sa.Column("id_usuario", sa.String(length=40), nullable=True),
        sa.Column("ip_origen", sa.String(length=100), nullable=True),
        sa.Column("motivo", sa.Text(), nullable=True),
        sa.Column("estado_anterior", sa.String(length=30), nullable=False),
        sa.Column("estado_nuevo", sa.String(length=30), nullable=False),
        sa.Column("politica_tipo", sa.String(length=50), nullable=True),
        sa.Column("dias_anticipacion", sa.Integer(), nullable=True),
        sa.Column("porcentaje_penalidad", sa.Float(), nullable=True),
        sa.Column("monto_pagado", sa.Float(), nullable=True),
        sa.Column("monto_reembolso", sa.Float(), nullable=True),
        sa.Column("refund_status", sa.String(length=50), nullable=True),
        sa.Column("pms_status", sa.String(length=50), nullable=True),
        sa.Column("cancellation_reference", sa.String(length=100), nullable=False),
        sa.Column("origen", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_auditoria_cancelacion_reserva_id_reserva",
        "auditoria_cancelacion_reserva",
        ["id_reserva"],
    )
    op.create_index(
        "ix_auditoria_cancelacion_reserva_cancellation_reference",
        "auditoria_cancelacion_reserva",
        ["cancellation_reference"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_auditoria_cancelacion_reserva_cancellation_reference",
        table_name="auditoria_cancelacion_reserva",
    )
    op.drop_index(
        "ix_auditoria_cancelacion_reserva_id_reserva",
        table_name="auditoria_cancelacion_reserva",
    )
    op.drop_table("auditoria_cancelacion_reserva")
