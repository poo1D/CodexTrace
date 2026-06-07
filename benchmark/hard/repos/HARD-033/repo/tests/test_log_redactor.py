import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from log_redactor import SECRET, redact_event, redact_text


class LogRedactorTest(unittest.TestCase):
    def test_redacts_plain_token_value(self):
        self.assertEqual(
            redact_text("login token=abc123 user=ada"),
            f"login token={SECRET} user=ada",
        )

    def test_redacts_token_in_event_message(self):
        event = {"level": "info", "message": "token=abc123 accepted"}

        redacted = redact_event(event)

        self.assertEqual(redacted["message"], f"token={SECRET} accepted")
        self.assertEqual(event["message"], "token=abc123 accepted")


if __name__ == "__main__":
    unittest.main()
