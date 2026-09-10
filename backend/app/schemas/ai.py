from pydantic import BaseModel, Field
class ExtractionOutput(BaseModel):
    source: str | None = None
    customer_name: str | None = None
    customer_organization: str | None = None
    customer_email: str | None = None
    product_name: str | None = None
    product_strength: str | None = None
    batch_number: str | None = None
    manufacturing_date: str | None = None
    expiry_date: str | None = None
    complaint_type: str | None = None
    complaint_date: str | None = None
    affected_quantity: str | None = None
    originating_site: str | None = None
    impacted_materials: str | None = None
    description: str | None = None
    patient_impact: str | None = None
    safety_concern: bool | None = None
