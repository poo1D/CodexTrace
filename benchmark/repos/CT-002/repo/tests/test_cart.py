import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cart import discounted_total_cents


class CartTest(unittest.TestCase):
    def test_half_cent_rounds_up(self):
        self.assertEqual(discounted_total_cents([101], 50), 51)


if __name__ == "__main__":
    unittest.main()
