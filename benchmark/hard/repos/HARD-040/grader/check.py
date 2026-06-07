import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src"))


def run_visible_tests():
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(result.returncode)


import copy

run_visible_tests()
mod = importlib.import_module("ledger")

accounts = {
    "cash": {"currency": "USD", "balance": 100},
    "revenue": {"currency": "USD", "balance": 0},
    "_applied": {},
}
events = [
    {
        "id": "sale-1",
        "postings": [
            {"account": "cash", "amount": 30, "currency": "USD"},
            {"account": "revenue", "amount": -30, "currency": "USD"},
        ],
    }
]
accounts_before = copy.deepcopy(accounts)
events_before = copy.deepcopy(events)
result = mod.apply_events(accounts, events)
assert accounts == accounts_before
assert events == events_before
assert result["cash"]["balance"] == 130
assert result["revenue"]["balance"] == -30

result2 = mod.apply_events(result, events)
assert result2["cash"]["balance"] == 130
assert result2["revenue"]["balance"] == -30

reversed_once = mod.apply_events(
    result,
    [{"id": "void-1", "reversal_of": "sale-1"}],
)
assert reversed_once["cash"]["balance"] == 100
assert reversed_once["revenue"]["balance"] == 0
assert "void-1" in reversed_once.get("_applied", {})

try:
    mod.apply_events(reversed_once, [{"id": "void-2", "reversal_of": "sale-1"}])
except mod.LedgerError as error:
    assert "already reversed" in str(error)
else:
    raise AssertionError("expected LedgerError for duplicate reversal")

bad_accounts = {
    "cash": {"currency": "USD", "balance": 100},
    "revenue": {"currency": "USD", "balance": 0},
}
before_bad = copy.deepcopy(bad_accounts)
try:
    mod.apply_events(
        bad_accounts,
        [
            {
                "id": "bad-1",
                "postings": [
                    {"account": "cash", "amount": -10, "currency": "USD"},
                    {"account": "revenue", "amount": 10, "currency": "EUR"},
                ],
            }
        ],
    )
except mod.LedgerError as error:
    assert "currency" in str(error).lower()
else:
    raise AssertionError("expected LedgerError for currency mismatch")
assert bad_accounts == before_bad

try:
    mod.apply_events({"cash": {"currency": "USD", "balance": 5}}, [{"id": "missing", "reversal_of": "nope"}])
except mod.LedgerError as error:
    assert "unknown" in str(error).lower()
else:
    raise AssertionError("expected LedgerError for unknown reversal")
