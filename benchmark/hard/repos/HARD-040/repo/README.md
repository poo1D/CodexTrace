# ledger-reconciler

`apply_events(accounts, events)` applies ledger events and
returns a new accounts dictionary.

Account shape:

```python
{"cash": {"currency": "USD", "balance": 100}}
```

Event shape:

```python
{
    "id": "evt-1",
    "postings": [
        {"account": "cash", "amount": -10, "currency": "USD"},
        {"account": "revenue", "amount": 10, "currency": "USD"},
    ],
}
```

Requirements:

- Apply a batch atomically: failed events leave all balances unchanged.
- Ignore duplicate event ids that were already applied.
- A reversal event has `reversal_of` and negates the original event once.
- Currency mismatches raise `LedgerError`.
- Inputs must not be mutated.
