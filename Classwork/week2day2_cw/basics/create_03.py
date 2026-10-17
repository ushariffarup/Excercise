import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting the database at {DATABASE_URL}")

invoice_id = {"invoice_id": "INV_201",
              "vendor": "UMAR",
              "amount": 100.0,
              "status": "PAID",
              "approval": "MANAGER_REVIEW"
              }

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO invoices (invoice_id, vendor, amount, status, approval) VALUES (%(invoice_id)s, %(vendor)s, %(amount)s, %(status)s, %(approval)s);",
            invoice_id
        )
        conn.commit()