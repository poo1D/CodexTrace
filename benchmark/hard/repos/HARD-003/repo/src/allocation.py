def allocate_cents(total_cents, weights):
    total_weight = sum(weights)
    if total_weight == 0:
        return [0 for _ in weights]
    return [round(total_cents * weight / total_weight) for weight in weights]
