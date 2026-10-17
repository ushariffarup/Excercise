import json

DATA_FILE= "invoice.json"
PAYMENT_FILE= "payment.json"

def load_invoices():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def load_payments():
    with open(PAYMENT_FILE, "r") as f:
        return json.load(f)     
def save_invoices(invoices):
    with open(DATA_FILE, "w") as f:
        json.dump(invoices, f, indent=4)

def save_payments(payments):
    with open(PAYMENT_FILE, "w") as f:
        json.dump(payments, f, indent=4)

def get_invoice_by_id(invoice_id):
    invoices = load_invoices()
    for invoice in invoices:
        if invoice["invoice_id"] == invoice_id:
            return invoice
    return None

def get_payment_by_id(payment_id):
    payments = load_payments()
    for payment in payments:
        if payment["payment_id"] == payment_id:
            return payment
    return None

def add_invoice(invoice):
    invoices = load_invoices()
    invoices.append(invoice)
    save_invoices(invoices)

def add_payment(payment):
    payments = load_payments()
    payments.append(payment)
    save_payments(payments)

def update_invoice(invoice_id, updated_invoice):
    invoices = load_invoices()
    for i, invoice in enumerate(invoices):
        if invoice["invoice_id"] == invoice_id:
            invoices[i] = updated_invoice
            save_invoices(invoices)
            return True
    return False

def update_payment(payment_id, updated_payment):
    payments = load_payments()
    for i, payment in enumerate(payments):
        if payment["payment_id"] == payment_id:
            payments[i] = updated_payment
            save_payments(payments)
            return True
    return False    

def delete_invoice(invoice_id):
    invoices = load_invoices()
    for i, invoice in enumerate(invoices):
        if invoice["invoice_id"] == invoice_id:
            del invoices[i]
            save_invoices(invoices)
            return True
    return False

def delete_payment(payment_id):
    payments = load_payments()
    for i, payment in enumerate(payments):
        if payment["payment_id"] == payment_id:
            del payments[i]
            save_payments(payments)
            return True
    return False