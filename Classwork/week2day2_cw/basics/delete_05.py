import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting the database at {DATABASE_URL}")

invoice_id = {"invoice_id": "INV_201"}

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM invoices WHERE invoice_id = %(invoice_id)s;",
            invoice_id
        )
        conn.commit()