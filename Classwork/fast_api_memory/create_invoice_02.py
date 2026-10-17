from fastapi import APIRouter
from Classwork.fast_api_memory.data_store import invoices
from Classwork.fast_api_memory.models import Invoice  

router = APIRouter()

@router.post("/invoices")
def create_invoice(invoice: Invoice):
    new_invoice = invoice.model_dump()
    invoices.append(new_invoice)
    return {"message": "Invoice created successfully","invoice": new_invoice}