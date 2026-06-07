import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from time_window import overlaps


class TimeWindowTest(unittest.TestCase):
    def test_touching_half_open_windows_do_not_overlap(self):
        left = (datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 10, 0))
        right = (datetime(2026, 1, 1, 10, 0), datetime(2026, 1, 1, 11, 0))
        self.assertFalse(overlaps(left, right))

    def test_actual_overlap(self):
        left = (datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 10, 30))
        right = (datetime(2026, 1, 1, 10, 0), datetime(2026, 1, 1, 11, 0))
        self.assertTrue(overlaps(left, right))


if __name__ == "__main__":
    unittest.main()
