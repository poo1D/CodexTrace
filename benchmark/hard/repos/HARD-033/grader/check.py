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


run_visible_tests()
mod = importlib.import_module("log_redactor")
replacement = mod.SECRET

assert mod.redact_text("password=hunter2 token=abc") == f"password={replacement} token={replacement}"
assert mod.redact_text("GET /v1?apiKey=key-123&query=ok") == f"GET /v1?apiKey={replacement}&query=ok"
assert mod.redact_text("Authorization: Bearer sk-live-123") == f"Authorization: Bearer {replacement}"
assert mod.redact_text("AUTHORIZATION=Basic abcdef") == f"AUTHORIZATION=Basic {replacement}"

original = {
    "level": "info",
    "message": "request password=hunter2",
    "headers": {
        "Authorization": "Bearer sk-live-123",
        "X-Trace": "keep-me",
    },
    "context": {
        "apiKey": "key-123",
        "nested": [{"Password": "credential"}, {"safe": "value"}],
    },
}
expected_original = {
    "level": "info",
    "message": "request password=hunter2",
    "headers": {
        "Authorization": "Bearer sk-live-123",
        "X-Trace": "keep-me",
    },
    "context": {
        "apiKey": "key-123",
        "nested": [{"Password": "credential"}, {"safe": "value"}],
    },
}

redacted = mod.redact_event(original)
assert redacted["message"] == f"request password={replacement}"
assert redacted["headers"]["Authorization"] == f"Bearer {replacement}"
assert redacted["headers"]["X-Trace"] == "keep-me"
assert redacted["context"]["apiKey"] == replacement
assert redacted["context"]["nested"][0]["Password"] == replacement
assert redacted["context"]["nested"][1]["safe"] == "value"
assert original == expected_original

assert mod.redact_event({"token": "abc", "user": "ada"}) == {
    "token": replacement,
    "user": "ada",
}
