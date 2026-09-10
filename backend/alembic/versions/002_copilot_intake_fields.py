"""Add fields used by the copilot-led complaint intake."""
from alembic import op
import sqlalchemy as sa

revision = '002_copilot_intake_fields'
down_revision = '001_initial'

def upgrade():
    op.add_column('complaints', sa.Column('originating_site', sa.String(120)))
    op.add_column('complaints', sa.Column('impacted_materials', sa.String(240)))
    op.add_column('complaints', sa.Column('suggested_next_action', sa.String(240)))
    op.add_column('complaints', sa.Column('initial_risk_assessment', sa.Text()))

def downgrade():
    op.drop_column('complaints', 'initial_risk_assessment')
    op.drop_column('complaints', 'suggested_next_action')
    op.drop_column('complaints', 'impacted_materials')
    op.drop_column('complaints', 'originating_site')
