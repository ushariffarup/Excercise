invoices = [
    {"invoice_id": "INV-101", "amount": 85000, "status": "PENDING"},
    {"invoice_id": "INV-102", "amount": 142500, "status": "APPROVED"},
    {"invoice_id": "INV-103", "amount": 250000, "status": "PENDING"},
]


with open(DATA_FILE) as f:
    invoices = json.load(f)
 
# Exercise 1 - total amount by vendor
vendor_totals = {}
for invoice in invoices:
    vendor = invoice["vendor"]
    amount = invoice["amount"]
    vendor_totals[vendor] = vendor_totals.get(vendor, 0) + amount


# Exercise 2 - filter out duplicate invoices and print the duplicates alone
seen = []
duplicates = []
for invoice in invoices:
    if invoice in seen:
        duplicates.append(invoice)
    else:
        seen.append(invoice)
 
print(duplicates)  # Output: [{'invoice_id': 'INV-101', 'vendor': 'ABC Ltd.', 'amount': 1500.0, 'status': 'Paid'}]