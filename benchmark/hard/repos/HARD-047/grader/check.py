import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src"))


def run_visible_tests():
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(result.returncode)


import copy
import hashlib
import hmac

run_visible_tests()
mod = importlib.import_module("webhook_guard")


def sign(timestamp, body, key):
    message = f"{timestamp}.{body}".encode("utf-8")
    digest = hmac.new(
        key.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()
    return f"ignored=x, t={timestamp}, v1={digest}"


def make_event(tenant, event_id, timestamp, body, key):
    return {
        "tenant": tenant,
        "event_id": event_id,
        "timestamp": timestamp,
        "body": body,
        "signature": sign(timestamp, body, key),
    }


keys = {"tenant-a": "k1", "tenant-b": "k2"}
store = {}

raw_body = '{\n  "amount": 10,\n  "id": "evt_raw"\n}'
event = make_event("tenant-a", "evt_raw", 1000, raw_body, "k1")
original_event = copy.deepcopy(event)
original_keys = copy.deepcopy(keys)
assert mod.verify_event(event, keys, store, 1000) is True
assert event == original_event
assert keys == original_keys

replay = make_event("tenant-a", "evt_raw", 1000, raw_body, "k1")
try:
    mod.verify_event(replay, keys, store, 1000)
except mod.WebhookError as error:
    assert "replay" in str(error).lower()
else:
    raise AssertionError("same tenant replay was accepted")

other_tenant = make_event("tenant-b", "evt_raw", 1000, raw_body, "k2")
assert mod.verify_event(other_tenant, keys, store, 1000) is True

rotated_keys = {"tenant-a": ["old-key", "new-key"]}
rotated = make_event("tenant-a", "evt_rotated", 1000, '{"ok":true}', "new-key")
assert mod.verify_event(rotated, rotated_keys, store, 1000) is True

boundary = make_event("tenant-a", "evt_boundary", 700, '{"ok":true}', "k1")
assert mod.verify_event(boundary, keys, store, 1000) is True

bad = make_event("tenant-a", "evt_bad", 1000, '{"bad":true}', "k1")
bad["signature"] = "t=1000,v1=bad"
try:
    mod.verify_event(bad, keys, store, 1000)
except mod.WebhookError:
    pass
else:
    raise AssertionError("bad signature was accepted")
fixed = make_event("tenant-a", "evt_bad", 1000, '{"bad":true}', "k1")
assert mod.verify_event(fixed, keys, store, 1000) is True

expired = make_event("tenant-a", "evt_expired", 1000, '{"old":true}', "k1")
assert mod.verify_event(expired, keys, store, 1000) is True
fresh = make_event("tenant-a", "evt_fresh", 1299, '{"fresh":true}', "k1")
assert mod.verify_event(fresh, keys, store, 1300) is True
later = make_event("tenant-a", "evt_later", 1600, '{"later":true}', "k1")
assert mod.verify_event(later, keys, store, 1600) is True
expired_again = make_event("tenant-a", "evt_expired", 1600, '{"old":true}', "k1")
assert mod.verify_event(expired_again, keys, store, 1600) is True

mismatch = make_event("tenant-a", "evt_mismatch", 1000, '{"x":1}', "k1")
mismatch["signature"] = sign(999, '{"x":1}', "k1")
try:
    mod.verify_event(mismatch, keys, store, 1000)
except mod.WebhookError as error:
    assert "timestamp" in str(error).lower()
else:
    raise AssertionError("mismatched signature timestamp was accepted")
