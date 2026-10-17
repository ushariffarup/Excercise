import psycopg
import os
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to database at {DATABASE_URL}")


with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * from invoices")
        invoices = cur.fetchall()


for invoice in invoices:
        print(invoice)              

import psycopg
import os
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to database at {DATABASE_URL}")


invoice = {
    "invoice_id": "INV-201",
    "vendor": "Acme Corp",
    "amount": 1500.00,
    "status": "pending",
    "approval": "MANAGER_REVIEW"
}


with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("Insert into invoices (invoice_id, vendor, amount, status, approval) values (%s, %s, %s, %s, %s)", 
                    (invoice["invoice_id"], invoice["vendor"], invoice["amount"], invoice["status"], invoice["approval"]))
        conn.commit()
        print("Invoice created successfully.")