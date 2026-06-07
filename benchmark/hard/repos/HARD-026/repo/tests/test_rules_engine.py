import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rules_engine import evaluate


class RulesEngineTest(unittest.TestCase):
    def test_highest_priority_matching_rule_wins(self):
        rules = [
            {"conditions": {"country": "US"}, "result": "review", "priority": 1},
            {"conditions": {"country": "US", "amount": 5000}, "result": "block", "priority": 10},
        ]
        self.assertEqual(evaluate({"country": "US", "amount": 5000}, rules), "block")

    def test_legacy_rule_is_fallback_when_no_priority_rule_matches(self):
        rules = [
            {"conditions": {"country": "US"}, "result": "legacy-review"},
            {"conditions": {"country": "CA"}, "result": "priority-review", "priority": 5},
        ]
        self.assertEqual(evaluate({"country": "US"}, rules), "legacy-review")


if __name__ == "__main__":
    unittest.main()
