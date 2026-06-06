import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from password_policy import validation_errors


class PasswordPolicyTest(unittest.TestCase):
    def test_valid_password(self):
        self.assertEqual(validation_errors("VeryGood123!"), [])


if __name__ == "__main__":
    unittest.main()
