import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from search_index import search


class SearchIndexTest(unittest.TestCase):
    def test_prefix_matches_only(self):
        items = ["car", "cart", "scar", "dog"]
        self.assertEqual(search(items, "car"), ["car", "cart"])

    def test_exact_match_ranks_first(self):
        items = ["cart", "car", "carbon"]
        self.assertEqual(search(items, "car"), ["car", "carbon", "cart"])


if __name__ == "__main__":
    unittest.main()
