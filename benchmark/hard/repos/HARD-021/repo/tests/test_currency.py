import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from currency import CurrencyParseError, parse_cents


class CurrencyParserTest(unittest.TestCase):
    def test_simple_dollar_amount(self):
        self.assertEqual(parse_cents("$12.34"), 1234)

    def test_thousands_separator(self):
        self.assertEqual(parse_cents("$1,234.50"), 123450)

    def test_invalid_text_raises_domain_error(self):
        with self.assertRaises(CurrencyParseError):
            parse_cents("not money")


if __name__ == "__main__":
    unittest.main()
