import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from allocation import allocate_cents


class AllocationTest(unittest.TestCase):
    def test_largest_remainder(self):
        self.assertEqual(allocate_cents(10, [1, 1, 1]), [4, 3, 3])


if __name__ == "__main__":
    unittest.main()
