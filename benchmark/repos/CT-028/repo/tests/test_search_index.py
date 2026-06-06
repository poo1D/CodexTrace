import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from search_index import SearchIndex


class SearchIndexTest(unittest.TestCase):
    def test_prefix_and_exact_ranking(self):
        index = SearchIndex(["carpet", "car", "cart", "dog"])
        self.assertEqual(index.search("car"), ["car", "carpet", "cart"])


if __name__ == "__main__":
    unittest.main()
