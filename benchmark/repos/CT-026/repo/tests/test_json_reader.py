import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from json_reader import read_json


class JsonReaderTest(unittest.TestCase):
    def test_empty_file_is_empty_object(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            path = handle.name
        self.assertEqual(read_json(path), {})


if __name__ == "__main__":
    unittest.main()
