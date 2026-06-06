import sys
import unittest
from datetime import timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from date_utils import parse_iso_datetime


class DateTest(unittest.TestCase):
    def test_z_suffix_is_utc(self):
        parsed = parse_iso_datetime("2026-06-05T12:30:00Z")
        self.assertEqual(parsed.tzinfo, timezone.utc)


if __name__ == "__main__":
    unittest.main()
