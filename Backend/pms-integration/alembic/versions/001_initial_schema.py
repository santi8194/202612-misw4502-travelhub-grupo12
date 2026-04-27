"""Initial pms integration schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-04-22 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reservations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("reservation_id", sa.String(), nullable=True),
        sa.Column("room_id", sa.String(), nullable=True),
        sa.Column("room_type", sa.String(), nullable=True),
        sa.Column("guest_name", sa.String(), nullable=True),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("hotel_id", sa.String(), nullable=True),
        sa.Column("fecha_reserva", sa.String(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
    )

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "CREATE UNIQUE INDEX idx_room_date_active ON reservations (room_id, fecha_reserva) WHERE state <> 'CANCELLED'"
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS idx_room_date_active")
    op.drop_table("reservations")
