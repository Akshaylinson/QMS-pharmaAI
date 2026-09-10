from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Any
class ComplaintBase(BaseModel):
    source: str | None = None; customer_name: str | None = None; customer_organization: str | None = None; customer_contact: str | None = None; customer_email: str | None = None; country_region: str | None = None
    product_name: str | None = None; product_strength: str | None = None; batch_number: str | None = None; manufacturing_date: date | None = None; expiry_date: date | None = None; product_type: str | None = None; market_country: str | None = None
    originating_site: str | None = None; impacted_materials: str | None = None
    complaint_type: str | None = None; complaint_date: date | None = None; received_date: date | None = None; description: str | None = None; product_condition: str | None = None; affected_quantity: str | None = None; sample_available: bool | None = None; patient_impact: str | None = None; quality_impact: str | None = None; regulatory_impact: str | None = None; safety_concern: bool | None = None; severity: str | None = None; priority: str | None = None; risk_level: str | None = None; suggested_next_action: str | None = None; initial_risk_assessment: str | None = None; status: str = 'PENDING_REVIEW'
    @field_validator('manufacturing_date','expiry_date','complaint_date','received_date',mode='before')
    @classmethod
    def accept_month_year_dates(cls,value):
        """Complaint reports frequently provide a month/year instead of a day."""
        if value == '' or value is None: return None
        if isinstance(value,str):
            for pattern in ('%B %Y','%b %Y','%d/%m/%Y','%d-%m-%Y','%m/%d/%Y','%m-%d-%Y','%Y-%m-%d'):
                try: return datetime.strptime(value,pattern).date()
                except ValueError: pass
        return value
class ComplaintCreate(ComplaintBase): pass
class ComplaintUpdate(ComplaintBase): status: str | None = None
class ComplaintOut(ComplaintBase):
    model_config = ConfigDict(from_attributes=True)
    id: str; complaint_number: str; created_at: datetime; updated_at: datetime
class IntakeRequest(BaseModel):
    raw_input: str = Field(min_length=3)
    source_type: str = 'text'
    current_complaint: dict[str, Any] = Field(default_factory=dict)
class CopilotRequest(BaseModel): question: str; complaint: dict[str, Any]
