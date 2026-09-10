"""Store complaint date-like intake values as text without normalizing them."""
from alembic import op
import sqlalchemy as sa

revision = '003_preserve_intake_values'
down_revision = '002_copilot_intake_fields'

DATE_FIELDS = ('manufacturing_date', 'expiry_date', 'complaint_date', 'received_date')


def upgrade():
    # batch_alter_table supports SQLite as well as PostgreSQL. PostgreSQL needs
    # an explicit cast because existing columns are DATE typed.
    with op.batch_alter_table('complaints') as batch_op:
        for field in DATE_FIELDS:
            batch_op.alter_column(
                field,
                existing_type=sa.Date(),
                type_=sa.Text(),
                postgresql_using=f'{field}::text',
            )


def downgrade():
    # A free-form value cannot always be safely converted back into a DATE.
    # Keeping it as text is intentionally irreversible without QA data review.
    raise RuntimeError('Date-like complaint values must be reviewed before converting them back to DATE columns.')
