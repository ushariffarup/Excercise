import Classwork.week2day2_cw.refector.repository as repository
from Classwork.week2day2_cw.refector.models import Invoice

def get_invoice(invoice_id: str) -> Invoice:
    print(f"Fetching invoice with ID from service: {invoice_id}")
    invoice_data = repository.get_invoice_by_id(invoice_id)
    print(f"Retrieved invoice data from repository: {invoice_data}")
    if invoice_data is None:
        raise ValueError(f"Invoice with ID {invoice_id} not found")
    return Invoice(**invoice_data)

def create_invoice(invoice_data: dict) -> Invoice:
    new_invoice = Invoice(**invoice_data)
    repository.add_invoice(new_invoice.dict())
    return new_invoice

def update_invoice(invoice_id: str, updated_data: dict) -> Invoice:
    existing_invoice = repository.get_invoice_by_id(invoice_id)
    print(f"Existing invoice data from repository: {existing_invoice}")
    if existing_invoice is None:
        raise ValueError(f"Invoice with ID {invoice_id} not found")
    #updated_invoice = Invoice(**existing_invoice, **updated_data)
    merged_data = {**existing_invoice, **updated_data, "invoice_id": invoice_id}
    updated_invoice = Invoice(**merged_data)
    repository.update_invoice(invoice_id, updated_invoice.dict())
    print(f"Updated invoice data to be saved to repository: {updated_invoice.dict()}")
    return updated_invoice

def delete_invoice(invoice_id: str) -> None:
    existing_invoice = repository.get_invoice_by_id(invoice_id)
    if existing_invoice is None:
        raise ValueError(f"Invoice with ID {invoice_id} not found")
    repository.delete_invoice(invoice_id)