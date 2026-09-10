"""Add fields used by the copilot-led complaint intake."""
from alembic import op
import sqlalchemy as sa

revision = '002_copilot_intake_fields'
down_revision = '001_initial'

def upgrade():
    existing={column['name'] for column in sa.inspect(op.get_bind()).get_columns('complaints')}
    additions={
        'originating_site': sa.String(120),
        'impacted_materials': sa.String(240),
        'suggested_next_action': sa.String(240),
        'initial_risk_assessment': sa.Text(),
    }
    for name, column_type in additions.items():
        if name not in existing:
            op.add_column('complaints', sa.Column(name, column_type))

def downgrade():
    op.drop_column('complaints', 'initial_risk_assessment')
    op.drop_column('complaints', 'suggested_next_action')
    op.drop_column('complaints', 'impacted_materials')
    op.drop_column('complaints', 'originating_site')
