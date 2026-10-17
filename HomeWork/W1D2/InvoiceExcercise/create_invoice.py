from fastapi import APIRouter
from HomeWork.W1D2.InvoiceExcercise.datastore import invoices
from HomeWork.W1D2.InvoiceExcercise.models import Invoice

router = APIRouter()

@router.post("/invoices")
def create_invoice(invoice: Invoice):
    new_invoice = invoice.model_dump()
    invoices.append(new_invoice)
    return new_invoice