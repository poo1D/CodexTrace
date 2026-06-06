import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from csv_records import parse_records


class CsvRecordTest(unittest.TestCase):
    def test_quoted_comma(self):
        self.assertEqual(parse_records('name,note\nAda,"ships, fast"'), [["name", "note"], ["Ada", "ships, fast"]])


if __name__ == "__main__":
    unittest.main()
