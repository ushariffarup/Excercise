invoices = {
        "invoice_id": 1,
        "amount": 1200,
        "status": "pending"
    }

#print(invoices["vendor"])
print(invoices.get("vendor","UNKNOWN"))