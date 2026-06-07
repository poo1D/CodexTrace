import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from retry_policy import plan_retries


class RetryPolicyTest(unittest.TestCase):
    def test_exponential_backoff(self):
        response = {"status": 503, "headers": {}}

        self.assertEqual(plan_retries(response, attempts=3), [1, 2, 4])

    def test_base_delay_is_configurable(self):
        response = {"status": 503, "headers": {}}

        self.assertEqual(plan_retries(response, attempts=2, base_delay=3), [3, 6])

    def test_zero_attempts_returns_empty_plan(self):
        response = {"status": 503, "headers": {}}

        self.assertEqual(plan_retries(response, attempts=0), [])


if __name__ == "__main__":
    unittest.main()
