from fastapi import APIRouter
from HomeWork.W1D2.InvoiceExcercise.datastore import invoices

router = APIRouter()

@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: str):
    for i, invoice in enumerate(invoices):
        if invoice["invoice_id"] == invoice_id:
            deleted_invoice = invoices.pop(i)
            return deleted_invoice
    return {"error": "Invoice not found"}