"""Add gateway reference and Wompi transaction metadata to payments.

Revision ID: 002_payment_gateway_fields
Revises: 001_initial_schema
Create Date: 2026-05-03 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_payment_gateway_fields"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("reference", sa.String(), nullable=True))
    op.add_column("payments", sa.Column("wompi_transaction_id", sa.String(), nullable=True))
    op.add_column("payments", sa.Column("created_at", sa.String(), nullable=True))
    op.add_column("payments", sa.Column("updated_at", sa.String(), nullable=True))
    op.add_column("payments", sa.Column("event_published", sa.Boolean(), nullable=True, server_default=sa.false()))
    op.create_index("ix_payments_reference", "payments", ["reference"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_payments_reference", table_name="payments")
    op.drop_column("payments", "event_published")
    op.drop_column("payments", "updated_at")
    op.drop_column("payments", "created_at")
    op.drop_column("payments", "wompi_transaction_id")
    op.drop_column("payments", "reference")
