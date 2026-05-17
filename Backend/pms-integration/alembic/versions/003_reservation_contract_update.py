"""update reservation contract fields

Revision ID: 003_reservation_contract_update
Revises: 002
Create Date: 2026-05-17

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003_reservation_contract_update"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.execute("DROP INDEX IF EXISTS idx_room_date_active")

    op.add_column("reservations", sa.Column("id_categoria", sa.String(), nullable=True))
    op.add_column("reservations", sa.Column("id_usuario", sa.String(), nullable=True))
    op.add_column("reservations", sa.Column("hotel_code", sa.String(), nullable=True))
    op.add_column("reservations", sa.Column("room_type_code", sa.String(), nullable=True))
    op.add_column("reservations", sa.Column("fecha_check_in", sa.String(), nullable=True))
    op.add_column("reservations", sa.Column("fecha_check_out", sa.String(), nullable=True))

    op.drop_column("reservations", "room_id")
    op.drop_column("reservations", "room_type")
    op.drop_column("reservations", "guest_name")
    op.drop_column("reservations", "fecha_reserva")

    if dialect == "postgresql":
        op.execute(
            "CREATE UNIQUE INDEX idx_categoria_range_active ON reservations "
            "(id_categoria, fecha_check_in, fecha_check_out) WHERE state <> 'CANCELLED'"
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.execute("DROP INDEX IF EXISTS idx_categoria_range_active")

    op.add_column("reservations", sa.Column("room_id", sa.String(), nullable=True))
    op.add_column("reservations", sa.Column("room_type", sa.String(), nullable=True))
    op.add_column("reservations", sa.Column("guest_name", sa.String(), nullable=True))
    op.add_column("reservations", sa.Column("fecha_reserva", sa.String(), nullable=True))

    op.drop_column("reservations", "id_categoria")
    op.drop_column("reservations", "id_usuario")
    op.drop_column("reservations", "hotel_code")
    op.drop_column("reservations", "room_type_code")
    op.drop_column("reservations", "fecha_check_in")
    op.drop_column("reservations", "fecha_check_out")

    if dialect == "postgresql":
        op.execute(
            "CREATE UNIQUE INDEX idx_room_date_active ON reservations "
            "(room_id, fecha_reserva) WHERE state <> 'CANCELLED'"
        )
