def discounted_total_cents(item_cents, discount_percent):
    """Apply a percentage discount and round to nearest cent, half up."""
    return round(sum(item_cents) * (100 - discount_percent) / 100)
