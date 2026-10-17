from fastapi import FastAPI, APIRouter
from Classwork.fast_api_memory.create_invoice_02 import router as create_invoice
from Classwork.fast_api_memory.get_invoices_01 import router as get_invoices

app = FastAPI()
app.include_router(create_invoice)
app.include_router(get_invoices)
