import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cache_stampede import TTLCache


class CacheStampedeTest(unittest.TestCase):
    def test_reuses_fresh_value_and_refreshes_after_ttl(self):
        now = [100.0]
        calls = []
        cache = TTLCache(now=lambda: now[0])

        self.assertEqual(cache.get_or_set("item", lambda: calls.append("a") or "first", ttl=5), "first")
        self.assertEqual(cache.get_or_set("item", lambda: calls.append("b") or "second", ttl=5), "first")

        now[0] = 106.0
        self.assertEqual(cache.get_or_set("item", lambda: calls.append("c") or "third", ttl=5), "third")
        self.assertEqual(calls, ["a", "c"])

    def test_concurrent_miss_uses_one_loader_call(self):
        cache = TTLCache(now=lambda: 10.0)
        entered = threading.Event()
        release = threading.Event()
        calls = []
        lock = threading.Lock()

        def loader():
            with lock:
                calls.append("load")
            entered.set()
            release.wait(timeout=2)
            return "shared"

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(cache.get_or_set, "shared-key", loader, 30) for _ in range(5)]
            self.assertTrue(entered.wait(timeout=1))
            time.sleep(0.05)
            release.set()
            self.assertEqual([future.result(timeout=1) for future in futures], ["shared"] * 5)

        self.assertEqual(calls, ["load"])


if __name__ == "__main__":
    unittest.main()
