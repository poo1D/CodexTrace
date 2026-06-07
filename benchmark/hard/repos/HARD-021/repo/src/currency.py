class CurrencyParseError(ValueError):
    pass


def parse_cents(value):
    text = str(value).strip()
    text = text.replace("$", "").replace(",", "")
    try:
        return int(round(float(text) * 100))
    except ValueError as exc:
        raise CurrencyParseError(f"invalid amount: {value}") from exc
