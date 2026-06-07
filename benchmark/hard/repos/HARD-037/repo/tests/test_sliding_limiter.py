import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sliding_limiter import SlidingLimiter


class SlidingLimiterTest(unittest.TestCase):
    def test_allows_until_limit(self):
        limiter = SlidingLimiter(limit=2, window_seconds=10)

        self.assertTrue(limiter.allow("ada", now=100))
        self.assertTrue(limiter.allow("ada", now=101))
        self.assertFalse(limiter.allow("ada", now=102))

    def test_new_window_allows_again(self):
        limiter = SlidingLimiter(limit=1, window_seconds=10)

        self.assertTrue(limiter.allow("ada", now=100))
        self.assertFalse(limiter.allow("ada", now=101))
        self.assertTrue(limiter.allow("ada", now=110))

    def test_uses_clock_when_now_is_omitted(self):
        values = iter([200])
        limiter = SlidingLimiter(limit=1, window_seconds=10, clock=lambda: next(values))

        self.assertTrue(limiter.allow("ada"))


if __name__ == "__main__":
    unittest.main()
