import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rate_limiter import SlidingWindowLimiter


class RateLimiterTest(unittest.TestCase):
    def test_allowlisted_user_bypasses_limit(self):
        limiter = SlidingWindowLimiter(1, 60, allowlist={"admin"})
        self.assertTrue(limiter.allow("admin", 1))
        self.assertTrue(limiter.allow("admin", 2))


if __name__ == "__main__":
    unittest.main()
