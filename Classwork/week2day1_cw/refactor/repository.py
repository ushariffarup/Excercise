import json

DATA_FILE = "invoices.json"

def load_invoices():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def save_invoices(invoices):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(invoices, file, indent=4)

def get_invoice_by_id(invoice_id):
    print(f"Fetching invoice with ID from repository: {invoice_id}")
    invoices = load_invoices()
    print(f"Loaded {len(invoices)} invoices from repository")
    for invoice in invoices:
        if invoice["invoice_id"] == invoice_id:
            return invoice
    return None

def add_invoice(invoice):
    invoices = load_invoices()
    invoices.append(invoice)
    save_invoices(invoices)

def update_invoice(invoice_id, updated_invoice):
    invoices = load_invoices()
    for i, invoice in enumerate(invoices):
        if invoice["invoice_id"] == invoice_id:
            invoices[i] = updated_invoice
            save_invoices(invoices)
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
