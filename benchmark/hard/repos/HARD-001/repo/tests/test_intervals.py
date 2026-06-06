import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from intervals import merge_intervals


class IntervalTest(unittest.TestCase):
    def test_touching_half_open_intervals_stay_separate(self):
        self.assertEqual(merge_intervals([(1, 3), (3, 5)]), [(1, 3), (3, 5)])

    def test_overlap_merges(self):
        self.assertEqual(merge_intervals([(5, 7), (1, 4), (3, 6)]), [(1, 7)])


if __name__ == "__main__":
    unittest.main()
