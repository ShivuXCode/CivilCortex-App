"""add_performance_indexes

Revision ID: 7ef9635f7c4e
Revises: 1990d91f683b
Create Date: 2026-09-16 15:15:35.098522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ef9635f7c4e'
down_revision: Union[str, Sequence[str], None] = '1990d91f683b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('ix_buildings_organization_id', 'buildings', ['organization_id'])
    op.create_index('ix_floors_building_id', 'floors', ['building_id'])
    op.create_index('ix_areas_floor_id', 'areas', ['floor_id'])
    op.create_index('ix_structural_elements_area_id', 'structural_elements', ['area_id'])
    op.create_index('ix_inspections_building_id', 'inspections', ['building_id'])
    op.create_index('ix_defects_structural_element_id', 'defects', ['structural_element_id'])
    op.create_index('ix_crack_observations_inspection_id', 'crack_observations', ['inspection_id'])
    op.create_index('ix_assessments_observation_id', 'assessments', ['observation_id'])
    op.create_index('ix_analysis_jobs_image_id', 'analysis_jobs', ['image_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_analysis_jobs_image_id', table_name='analysis_jobs')
    op.drop_index('ix_assessments_observation_id', table_name='assessments')
    op.drop_index('ix_crack_observations_inspection_id', table_name='crack_observations')
    op.drop_index('ix_defects_structural_element_id', table_name='defects')
    op.drop_index('ix_inspections_building_id', table_name='inspections')
    op.drop_index('ix_structural_elements_area_id', table_name='structural_elements')
    op.drop_index('ix_areas_floor_id', table_name='areas')
    op.drop_index('ix_floors_building_id', table_name='floors')
    op.drop_index('ix_buildings_organization_id', table_name='buildings')
