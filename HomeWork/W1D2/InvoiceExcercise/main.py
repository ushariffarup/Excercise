from fastapi import FastAPI
from HomeWork.W1D2.InvoiceExcercise.get_invoices import router as get_invoices_router
from HomeWork.W1D2.InvoiceExcercise.create_invoice import router as create_invoice_router
from HomeWork.W1D2.InvoiceExcercise.delete_invoice import router as delete_invoice_router

app = FastAPI()

app.include_router(get_invoices_router)
app.include_router(create_invoice_router)
app.include_router(delete_invoice_router)