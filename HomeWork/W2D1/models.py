from pydantic import BaseModel

class Invoice(BaseModel):
    invoice_id: int
    vendor: str
    amount: float
    status: str
    date: str

class Payment(BaseModel):
    invoice_id: int
    paid: float