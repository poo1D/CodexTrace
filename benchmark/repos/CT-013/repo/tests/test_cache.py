import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cache import TTLCache


class CacheTest(unittest.TestCase):
    def test_hit_before_expiry(self):
        now = [10]
        cache = TTLCache(lambda: now[0])
        cache.set("a", 1, ttl=5)
        self.assertEqual(cache.get("a"), 1)


if __name__ == "__main__":
    unittest.main()
