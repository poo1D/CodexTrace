def is_settled(payment):
    return payment.get('settled', False)
