import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ledger import apply_events


class LedgerTest(unittest.TestCase):
    def test_applies_balanced_event(self):
        accounts = {
            "cash": {"currency": "USD", "balance": 100},
            "revenue": {"currency": "USD", "balance": 0},
        }
        events = [
            {
                "id": "evt-1",
                "postings": [
                    {"account": "cash", "amount": -25, "currency": "USD"},
                    {"account": "revenue", "amount": 25, "currency": "USD"},
                ],
            }
        ]

        result = apply_events(accounts, events)

        self.assertEqual(result["cash"]["balance"], 75)
        self.assertEqual(result["revenue"]["balance"], 25)

    def test_creates_new_account(self):
        result = apply_events(
            {},
            [
                {
                    "id": "evt-1",
                    "postings": [
                        {"account": "cash", "amount": 5, "currency": "USD"},
                    ],
                }
            ],
        )

        self.assertEqual(result["cash"], {"currency": "USD", "balance": 5})


if __name__ == "__main__":
    unittest.main()
