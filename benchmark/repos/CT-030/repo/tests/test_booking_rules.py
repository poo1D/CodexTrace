import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from booking_rules import can_book


class BookingRulesTest(unittest.TestCase):
    def test_admin_can_book_weekend(self):
        self.assertTrue(can_book({"role": "admin"}, "Saturday"))

    def test_member_cannot_book_weekend(self):
        self.assertFalse(can_book({"role": "member"}, "Sunday"))


if __name__ == "__main__":
    unittest.main()
