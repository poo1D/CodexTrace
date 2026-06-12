import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cache_paths import write_cache


class CachePathTest(unittest.TestCase):
    def test_writes_repo_local_cache(self):
        path = write_cache("item.txt", "cached")
        self.assertEqual(path, Path(".cache") / "item.txt")
        self.assertEqual(path.read_text(encoding="utf-8"), "cached")


if __name__ == "__main__":
    unittest.main()
