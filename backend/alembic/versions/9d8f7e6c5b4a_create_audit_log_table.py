"""create_audit_log_table

Revision ID: 9d8f7e6c5b4a
Revises: 8c9d1a3b4e5f
Create Date: 2026-09-19 10:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9d8f7e6c5b4a'
down_revision: Union[str, Sequence[str], None] = '8c9d1a3b4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('previous_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_entity_id'), 'audit_logs', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_type'), 'audit_logs', ['entity_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
