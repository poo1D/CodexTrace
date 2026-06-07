import re


SECRET = "[REDACTED]"


def redact_text(text):
    return re.sub(r"(token=)[^\s&]+", r"\1" + SECRET, str(text))


def redact_event(event):
    redacted = dict(event)
    message = redacted.get("message")
    if isinstance(message, str):
        redacted["message"] = redact_text(message)
    return redacted
