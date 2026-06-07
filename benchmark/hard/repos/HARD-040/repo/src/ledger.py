class LedgerError(Exception):
    pass


def apply_events(accounts, events):
    result = accounts.copy()
    for event in events:
        for posting in event.get("postings", []):
            account = posting["account"]
            amount = posting["amount"]
            currency = posting["currency"]
            if account not in result:
                result[account] = {"currency": currency, "balance": 0}
            result[account]["balance"] += amount
    return result
