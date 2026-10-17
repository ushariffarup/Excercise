def determine_approval(invoice_amount):
    if invoice_amount > 1000:
        return "Manager"
    elif invoice_amount > 500:
        return "Supervisor approval required"
    else:
        return "Standard approval required"