import hashlib
import hmac
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from webhook_guard import WebhookError, verify_event


def sign(timestamp, body, key):
    message = f"{timestamp}.{body}".encode("utf-8")
    digest = hmac.new(
        key.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={digest}"


def envelope(event_id="evt_1", timestamp=1000, body='{"amount":10}'):
    return {
        "tenant": "tenant-a",
        "event_id": event_id,
        "timestamp": timestamp,
        "body": body,
        "signature": sign(timestamp, body, "k1"),
    }


class WebhookGuardTest(unittest.TestCase):
    def test_accepts_valid_event(self):
        self.assertTrue(
            verify_event(envelope(), {"tenant-a": "k1"}, {}, 1000)
        )

    def test_rejects_replay(self):
        store = {}
        verify_event(envelope(), {"tenant-a": "k1"}, store, 1000)
        with self.assertRaises(WebhookError):
            verify_event(envelope(), {"tenant-a": "k1"}, store, 1000)

    def test_rejects_old_timestamp(self):
        with self.assertRaises(WebhookError):
            verify_event(envelope(timestamp=600), {"tenant-a": "k1"}, {}, 1000)

    def test_rejects_bad_signature(self):
        item = envelope()
        item["signature"] = "t=1000,v1=bad"
        with self.assertRaises(WebhookError):
            verify_event(item, {"tenant-a": "k1"}, {}, 1000)


if __name__ == "__main__":
    unittest.main()
