from fastapi import APIRouter
from HomeWork.W1D2.InvoiceExcercise.datastore import invoices

router = APIRouter()

@router.get("/invoices")
def get_invoices():
    return invoices