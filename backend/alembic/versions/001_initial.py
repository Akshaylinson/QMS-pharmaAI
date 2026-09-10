"""initial tables"""
from alembic import op
import sqlalchemy as sa
revision = '001_initial'
down_revision = None
def upgrade():
    # Earlier application releases created these tables with SQLAlchemy at
    # startup but did not create Alembic version records. Make this first
    # revision safe for those installations so their existing data survives.
    existing=sa.inspect(op.get_bind()).get_table_names()
    if 'complaints' not in existing:
        op.create_table('complaints', sa.Column('id', sa.String(36), primary_key=True), sa.Column('complaint_number', sa.String(32), nullable=False, unique=True), sa.Column('status', sa.String(24), nullable=False), sa.Column('source', sa.String(48)), sa.Column('customer_name', sa.String(120)), sa.Column('customer_organization', sa.String(160)), sa.Column('customer_contact', sa.String(80)), sa.Column('customer_email', sa.String(160)), sa.Column('country_region', sa.String(100)), sa.Column('product_name', sa.String(160)), sa.Column('product_strength', sa.String(80)), sa.Column('batch_number', sa.String(80)), sa.Column('manufacturing_date', sa.Date()), sa.Column('expiry_date', sa.Date()), sa.Column('product_type', sa.String(80)), sa.Column('market_country', sa.String(100)), sa.Column('complaint_type', sa.String(80)), sa.Column('complaint_date', sa.Date()), sa.Column('received_date', sa.Date()), sa.Column('description', sa.Text()), sa.Column('product_condition', sa.String(160)), sa.Column('affected_quantity', sa.String(80)), sa.Column('sample_available', sa.Boolean()), sa.Column('patient_impact', sa.String(24)), sa.Column('quality_impact', sa.String(24)), sa.Column('regulatory_impact', sa.String(24)), sa.Column('safety_concern', sa.Boolean()), sa.Column('severity', sa.String(24)), sa.Column('priority', sa.String(24)), sa.Column('risk_level', sa.String(24)), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False))
        for col in ['complaint_number','batch_number','product_name','customer_name','complaint_date','status']: op.create_index('ix_complaints_'+col, 'complaints', [col])
    if 'analysis_records' not in existing:
        op.create_table('analysis_records', sa.Column('id',sa.String(36),primary_key=True),sa.Column('complaint_id',sa.String(36),sa.ForeignKey('complaints.id'),nullable=False),sa.Column('analysis_type',sa.String(40),nullable=False),sa.Column('payload',sa.JSON(),nullable=False),sa.Column('provider',sa.String(40)),sa.Column('created_at',sa.DateTime(),nullable=False))
    if 'audit_logs' not in existing:
        op.create_table('audit_logs',sa.Column('id',sa.String(36),primary_key=True),sa.Column('complaint_id',sa.String(36),sa.ForeignKey('complaints.id')),sa.Column('action',sa.String(100),nullable=False),sa.Column('details',sa.JSON()),sa.Column('created_at',sa.DateTime(),nullable=False))
def downgrade():
    op.drop_table('audit_logs'); op.drop_table('analysis_records'); op.drop_table('complaints')
