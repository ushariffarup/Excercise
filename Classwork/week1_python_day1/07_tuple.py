invoices1= ({"customer": "John Doe", "amount": 5000, "status": "unpaid"}, 
            {"customer": "Umar Shariff", "amount": 1000, "status": "paid"}, 
            {"customer": "Jane Smith", "amount": 2000, "status": "unpaid"})

invoices1[0]['customer']='Anil Kumr'
#invoices1.append({"customer": "Rahil Shariff", "amount": 3000, "status": "unpaid"})

for invoice in invoices1:
    print(f"Customer: {invoice['customer']}, Amount: {invoice['amount']}, Status: {invoice['status']}")
