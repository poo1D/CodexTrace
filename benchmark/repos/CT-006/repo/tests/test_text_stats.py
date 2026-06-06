import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from text_stats import word_frequency


class TextStatsTest(unittest.TestCase):
    def test_case_and_punctuation(self):
        self.assertEqual(word_frequency("Hello, hello world!"), {"hello": 2, "world": 1})


if __name__ == "__main__":
    unittest.main()
