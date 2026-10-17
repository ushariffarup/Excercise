import psycopg
import os
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to database at {DATABASE_URL}")


payments = {
    "payment_id": "PAY-101",
    "invoice_id": "INV-201",
    "amount": 1500.00,
    "status": "completed"
}


with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("Insert into invoices (invoice_id, vendor, amount, status, approval) values (%s, %s, %s, %s, %s)", 
                    (invoice["invoice_id"], invoice["vendor"], invoice["amount"], invoice["status"], invoice["approval"]))
        conn.commit()
        print("Invoice created successfully.")