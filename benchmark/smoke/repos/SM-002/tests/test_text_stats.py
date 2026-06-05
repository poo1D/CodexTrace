import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from text_stats import word_frequency


class WordFrequencyTest(unittest.TestCase):
    def test_ignores_case_and_punctuation(self):
        self.assertEqual(word_frequency("Hello, hello world!"), {"hello": 2, "world": 1})

    def test_empty_text(self):
        self.assertEqual(word_frequency("..."), {})


if __name__ == "__main__":
    unittest.main()
