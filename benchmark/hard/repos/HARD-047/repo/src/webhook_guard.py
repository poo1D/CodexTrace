import hashlib
import hmac
import json


REPLAY_WINDOW_SECONDS = 300


class WebhookError(Exception):
    pass


def _parse_signature(header):
    parts = {}
    for item in header.split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            parts[key.strip()] = value.strip()
    return int(parts["t"]), parts["v1"]


def _canonical_body(body):
    parsed = json.loads(body)
    return json.dumps(parsed, sort_keys=True, separators=(",", ":"))


def verify_event(envelope, keys, store, now):
    tenant = envelope["tenant"]
    event_id = envelope["event_id"]
    timestamp = int(envelope["timestamp"])

    seen = store.setdefault("seen", set())
    if event_id in seen:
        raise WebhookError("replayed event")
    seen.add(event_id)

    if abs(now - timestamp) > REPLAY_WINDOW_SECONDS:
        raise WebhookError("timestamp outside replay window")

    header_timestamp, actual = _parse_signature(envelope["signature"])
    if header_timestamp != timestamp:
        raise WebhookError("timestamp mismatch")

    key = keys[tenant]
    body = _canonical_body(envelope["body"])
    message = f"{timestamp}.{body}".encode("utf-8")
    expected = hmac.new(
        key.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()

    if actual != expected:
        raise WebhookError("invalid signature")
    return True
