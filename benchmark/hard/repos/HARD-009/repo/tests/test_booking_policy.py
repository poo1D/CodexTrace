import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from booking_policy import can_book


class BookingPolicyTest(unittest.TestCase):
    def test_member_cannot_book_blackout(self):
        self.assertFalse(can_book({"role": "member"}, "2026-07-04", 3, [("2026-07-01", "2026-07-10")]))

    def test_admin_can_book_blackout_when_capacity_positive(self):
        self.assertTrue(can_book({"role": "admin"}, "2026-07-04", 1, [("2026-07-01", "2026-07-10")]))


if __name__ == "__main__":
    unittest.main()
