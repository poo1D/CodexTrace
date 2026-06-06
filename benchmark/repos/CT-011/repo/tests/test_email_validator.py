import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from email_validator import is_valid_email


class EmailValidatorTest(unittest.TestCase):
    def test_basic_email(self):
        self.assertTrue(is_valid_email("person@example.com"))


if __name__ == "__main__":
    unittest.main()
