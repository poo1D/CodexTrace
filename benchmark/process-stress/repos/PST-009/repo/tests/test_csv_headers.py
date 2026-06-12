import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from csv_headers import normalize_headers


class CsvHeaderTest(unittest.TestCase):
    def test_lower_option(self):
        self.assertEqual(normalize_headers([" Name "], lower=True), ["name"])


if __name__ == "__main__":
    unittest.main()
