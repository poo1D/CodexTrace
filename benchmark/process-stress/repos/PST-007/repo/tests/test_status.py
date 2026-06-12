import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from status import format_status


class StatusTest(unittest.TestCase):
    def test_void_takes_precedence(self):
        self.assertEqual(format_status({"paid": True, "void": True}), "void")


if __name__ == "__main__":
    unittest.main()
