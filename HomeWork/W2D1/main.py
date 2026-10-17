from fastapi import FastAPI, HTTPException
from models import Invoice, Payment
from services import create_invoice, create_payment, get_invoice_by_id, get_payment_by_id, update_invoice, update_payment, delete_invoice, delete_payment

app = FastAPI()

@app.post("/invoices/")
def api_create_invoice(invoice_id: int, customer: str, amount: float, status: str):
    return create_invoice(invoice_id, customer, amount, status)

@app.post("/payments/")
def api_create_payment(payment_id: int, invoice_id: int, amount: float, date: str):
    return create_payment(payment_id, invoice_id, amount, date)

@app.get("/invoices/{invoice_id}")
def api_get_invoice_by_id(invoice_id: int):
    invoice = get_invoice_by_id(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.get("/payments/{payment_id}")
def api_get_payment_by_id(payment_id: int):
    payment = get_payment_by_id(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.put("/invoices/{invoice_id}")
def api_update_invoice(invoice_id: int, customer: str, amount: float, status: str):
    if not update_invoice(invoice_id, customer, amount, status):
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice updated successfully"}

@app.put("/payments/{payment_id}")
def api_update_payment(payment_id: int, invoice_id: int, amount: float, date: str):
    if not update_payment(payment_id, invoice_id, amount, date):
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment updated successfully"}

@app.delete("/invoices/{invoice_id}")
def api_delete_invoice(invoice_id: int):
    if not delete_invoice(invoice_id):
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice deleted successfully"}

@app.delete("/payments/{payment_id}")
def api_delete_payment(payment_id: int):
    if not delete_payment(payment_id):
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}