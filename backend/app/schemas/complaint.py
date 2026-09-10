from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Any
class ComplaintBase(BaseModel):
    source: str | None = None; customer_name: str | None = None; customer_organization: str | None = None; customer_contact: str | None = None; customer_email: str | None = None; country_region: str | None = None
    product_name: str | None = None; product_strength: str | None = None; batch_number: str | None = None; manufacturing_date: date | None = None; expiry_date: date | None = None; product_type: str | None = None; market_country: str | None = None
    complaint_type: str | None = None; complaint_date: date | None = None; received_date: date | None = None; description: str | None = None; product_condition: str | None = None; affected_quantity: str | None = None; sample_available: bool | None = None; patient_impact: str | None = None; quality_impact: str | None = None; regulatory_impact: str | None = None; safety_concern: bool | None = None; severity: str | None = None; priority: str | None = None; risk_level: str | None = None; status: str = 'PENDING_REVIEW'
class ComplaintCreate(ComplaintBase): pass
class ComplaintUpdate(ComplaintBase): status: str | None = None
class ComplaintOut(ComplaintBase):
    model_config = ConfigDict(from_attributes=True)
    id: str; complaint_number: str; created_at: datetime; updated_at: datetime
class IntakeRequest(BaseModel): raw_input: str = Field(min_length=3); source_type: str = 'text'
class CopilotRequest(BaseModel): question: str; complaint: dict[str, Any]
