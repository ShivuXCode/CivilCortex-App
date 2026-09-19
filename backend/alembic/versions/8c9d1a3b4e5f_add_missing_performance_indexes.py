"""add_missing_performance_indexes

Revision ID: 8c9d1a3b4e5f
Revises: 7ef9635f7c4e
Create Date: 2026-09-19 09:59:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c9d1a3b4e5f'
down_revision: Union[str, Sequence[str], None] = '7ef9635f7c4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    op.create_index(op.f('ix_defects_status'), 'defects', ['status'], unique=False)
    op.create_index(op.f('ix_inspections_inspector_id'), 'inspections', ['inspector_id'], unique=False)
    op.create_index(op.f('ix_analysis_jobs_status'), 'analysis_jobs', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_analysis_jobs_status'), table_name='analysis_jobs')
    op.drop_index(op.f('ix_inspections_inspector_id'), table_name='inspections')
    op.drop_index(op.f('ix_defects_status'), table_name='defects')
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
