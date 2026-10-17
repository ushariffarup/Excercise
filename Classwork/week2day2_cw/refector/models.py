from pydantic import BaseModel

class Invoice(BaseModel):
    invoice_id: str
    vendor: str = "UNKNOWN"
    amount: float
    status: str
    approval: str = "MANAGER_REVIEW"