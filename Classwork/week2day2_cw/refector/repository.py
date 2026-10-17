from Classwork.week2day2_cw.refector.database import get_connection


def get_invoice_by_id(invoice_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM invoices WHERE invoice_id = %(invoice_id)s;",
                {"invoice_id": invoice_id}
            )
            return cur.fetchone()
        
def add_invoice(invoice):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO invoices (invoice_id, vendor, amount, status, approval) VALUES (%(invoice_id)s, %(vendor)s, %(amount)s, %(status)s, %(approval)s);",
                invoice
            )
            conn.commit()


def update_invoice(invoice_id, updated_invoice):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE invoices SET vendor = %(vendor)s, amount = %(amount)s, status = %(status)s, approval = %(approval)s WHERE invoice_id = %(invoice_id)s;",
                {**updated_invoice, "invoice_id": invoice_id}
            )
            conn.commit()
            return cur.rowcount > 0

def delete_invoice(invoice_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM invoices WHERE invoice_id = %(invoice_id)s;",
                {"invoice_id": invoice_id}
            )
            conn.commit()
            return cur.rowcount > 0
