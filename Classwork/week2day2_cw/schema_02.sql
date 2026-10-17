CREATE TABLE invoices (
    invoice_id VARCHAR(20) PRIMARY KEY,
    vendor VARCHAR(100) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(30) NOT NULL,
    approval VARCHAR(30) NOT NULL,
);