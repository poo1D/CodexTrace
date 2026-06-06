import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from calc import sum_prefix


class SumPrefixTest(unittest.TestCase):
    def test_n_is_count_not_last_index(self):
        self.assertEqual(sum_prefix([1, 2, 3, 4], 2), 3)

    def test_zero_items(self):
        self.assertEqual(sum_prefix([10, 20], 0), 0)


if __name__ == "__main__":
    unittest.main()
