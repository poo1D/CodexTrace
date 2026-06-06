import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from parser_model import parse_item


class ParserModelTest(unittest.TestCase):
    def test_count_is_int(self):
        self.assertEqual(parse_item({"name": "a", "count": "2"}).count, 2)


if __name__ == "__main__":
    unittest.main()
