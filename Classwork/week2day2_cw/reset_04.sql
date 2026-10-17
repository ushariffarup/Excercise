TRUNCATE TABLE invoices;

INSERT INTO invoices (invoice_id, vendor, amount, status, approval)

VALUES
    ('INV-101', 'ABC Ltd', 85000, 'PENDING', 'MANAGER_REVIEW'),
    ('INV-102', 'xyz corp', 142500, 'PENDING', 'FINANCE_REVIEW'),
    ('INV-103', 'Globex', -550000, 'PENDING', 'APPROVED');