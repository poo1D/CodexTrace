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


from datetime import datetime, timezone

run_visible_tests()
mod = importlib.import_module("http_client")
slept = []
statuses = [mod.Response(503, headers={"Retry-After": "Wed, 21 Oct 2030 07:28:00 GMT"}), mod.Response(200, "done")]

def client(url):
    return statuses.pop(0)

response = mod.request_with_retry(
    "https://example.invalid/no-network",
    client=client,
    max_attempts=3,
    sleep=slept.append,
    now=lambda: datetime(2030, 10, 21, 7, 27, 30, tzinfo=timezone.utc),
)
assert response.status == 200
assert response.body == "done"
assert slept == [30]

calls = []
response = mod.request_with_retry(
    "https://example.invalid/not-found",
    client=lambda url: calls.append(url) or mod.Response(404, "missing"),
    max_attempts=5,
    sleep=lambda delay: (_ for _ in ()).throw(AssertionError("should not sleep")),
)
assert response.status == 404
assert calls == ["https://example.invalid/not-found"]

try:
    mod.request_with_retry(
        "https://example.invalid/always-429",
        client=lambda url: mod.Response(429, headers={"Retry-After": "bad"}),
        max_attempts=2,
        sleep=lambda delay: None,
    )
except mod.RetryError as exc:
    assert "exhausted" in str(exc).lower()
else:
    raise AssertionError("exhausted retries should raise RetryError")
