from pydantic import BaseModel

class Invoice(BaseModel):
    invoice_id: int
    vendor: str = "UNKNOWN"
    amount: float
    status: str