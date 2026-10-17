invoices =[
    {
        "invoice_id": "INV-1",
        "vendor": "ABC Corp",
        "amount": 1200,
        "status": "pending"
    },
    {
        "invoice_id": "INV-2",
        "vendor": "XYZ Ltd",
        "amount": 1500,
        "status": "paid"
    },
    {
        "invoice_id": "INV-3",
        "vendor": "LMN Inc",
        "amount": 2000,
        "status": "pending"
    }
]

for index, invoice in enumerate(invoices):
    if invoice[2] ["invoice_id"] == 2:
        invoice[index]["invoice_id"] = "INV-2"
    print(index, invoice)