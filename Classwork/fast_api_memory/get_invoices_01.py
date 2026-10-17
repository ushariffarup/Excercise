from fastapi import APIRouter
from Classwork.fast_api_memory.data_store import invoices

router = APIRouter()

@router.get("/invoices")
def get_invoices():
    return invoices