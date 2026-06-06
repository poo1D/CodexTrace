def invoice_total(items, tax_rate):
    subtotal = sum(item["price_cents"] * item.get("quantity", 1) for item in items)
    tax = round(subtotal * tax_rate)
    return subtotal + tax
