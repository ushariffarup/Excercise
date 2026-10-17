import repository
from models import Invoice, Payment

def create_invoice(invoice_id, customer, amount, status):
    invoice = Invoice(invoice_id, customer, amount, status)
    repository.add_invoice(invoice.__dict__)
    return invoice

def create_payment(payment_id, invoice_id, amount, date):
    payment = Payment(payment_id, invoice_id, amount, date)
    repository.add_payment(payment.__dict__)
    return payment

def get_invoice_by_id(invoice_id):
    invoice_data = repository.get_invoice_by_id(invoice_id)
    if invoice_data:
        return Invoice(**invoice_data)
    return None

def get_payment_by_id(payment_id):
    payment_data = repository.get_payment_by_id(payment_id)
    if payment_data:
        return Payment(**payment_data)
    return None

def update_invoice(invoice_id, customer, amount, status):
    updated_invoice = Invoice(invoice_id, customer, amount, status)
    return repository.update_invoice(invoice_id, updated_invoice.__dict__)

def update_payment(payment_id, invoice_id, amount, date):
    updated_payment = Payment(payment_id, invoice_id, amount, date)
    return repository.update_payment(payment_id, updated_payment.__dict__)

def delete_invoice(invoice_id):
    return repository.delete_invoice(invoice_id)

def delete_payment(payment_id):
    return repository.delete_payment(payment_id)    