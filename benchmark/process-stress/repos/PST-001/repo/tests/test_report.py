import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from report import average_score


class ReportTest(unittest.TestCase):
    def test_average_multiple_rows(self):
        self.assertEqual(average_score([{"score": 10}, {"score": 20}]), 15)


if __name__ == "__main__":
    unittest.main()
