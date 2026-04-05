"""Create user sessions table

Revision ID: 006_create_user_sessions
Revises: 005_update_partner_id
Create Date: 2026-04-04 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "006_create_user_sessions"
down_revision = "005_update_partner_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=64), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('refresh_token_hash', name='uq_user_sessions_refresh_token_hash'),
    )
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_refresh_token_hash', 'user_sessions', ['refresh_token_hash'])


def downgrade() -> None:
    op.drop_index('ix_user_sessions_refresh_token_hash', table_name='user_sessions')
    op.drop_index('ix_user_sessions_user_id', table_name='user_sessions')
    op.drop_table('user_sessions')