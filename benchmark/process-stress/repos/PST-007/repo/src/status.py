def format_status(invoice):
    if invoice.get("paid"):
        return "paid"
    if invoice.get("void"):
        return "void"
    return "open"
