import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Complaint(Base):
    __tablename__ = 'complaints'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(24), default='PENDING_REVIEW', index=True)
    source: Mapped[str | None] = mapped_column(String(48)); customer_name: Mapped[str | None] = mapped_column(String(120), index=True); customer_organization: Mapped[str | None] = mapped_column(String(160)); customer_contact: Mapped[str | None] = mapped_column(String(80)); customer_email: Mapped[str | None] = mapped_column(String(160)); country_region: Mapped[str | None] = mapped_column(String(100))
    product_name: Mapped[str | None] = mapped_column(String(160), index=True); product_strength: Mapped[str | None] = mapped_column(String(80)); batch_number: Mapped[str | None] = mapped_column(String(80), index=True); manufacturing_date: Mapped[datetime | None] = mapped_column(Date); expiry_date: Mapped[datetime | None] = mapped_column(Date); product_type: Mapped[str | None] = mapped_column(String(80)); market_country: Mapped[str | None] = mapped_column(String(100))
    complaint_type: Mapped[str | None] = mapped_column(String(80)); complaint_date: Mapped[datetime | None] = mapped_column(Date, index=True); received_date: Mapped[datetime | None] = mapped_column(Date); description: Mapped[str | None] = mapped_column(Text); product_condition: Mapped[str | None] = mapped_column(String(160)); affected_quantity: Mapped[str | None] = mapped_column(String(80)); sample_available: Mapped[bool | None] = mapped_column(Boolean)
    patient_impact: Mapped[str | None] = mapped_column(String(24)); quality_impact: Mapped[str | None] = mapped_column(String(24)); regulatory_impact: Mapped[str | None] = mapped_column(String(24)); safety_concern: Mapped[bool | None] = mapped_column(Boolean); severity: Mapped[str | None] = mapped_column(String(24)); priority: Mapped[str | None] = mapped_column(String(24)); risk_level: Mapped[str | None] = mapped_column(String(24))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow); updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
class AnalysisRecord(Base):
    __tablename__ = 'analysis_records'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4())); complaint_id: Mapped[str] = mapped_column(ForeignKey('complaints.id')); analysis_type: Mapped[str] = mapped_column(String(40)); payload: Mapped[dict] = mapped_column(JSON); provider: Mapped[str | None] = mapped_column(String(40)); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4())); complaint_id: Mapped[str | None] = mapped_column(ForeignKey('complaints.id')); action: Mapped[str] = mapped_column(String(100)); details: Mapped[dict | None] = mapped_column(JSON); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
