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
import datetime as dt
import email.utils

run_visible_tests()
mod = importlib.import_module("retry_policy")

assert mod.plan_retries({"status": 400, "headers": {}}, attempts=3) == []
assert mod.plan_retries({"status": 404, "headers": {}}, attempts=3) == []
assert mod.plan_retries({"status": 409, "headers": {}}, attempts=2) == [1, 2]
assert mod.plan_retries({"status": 500, "headers": {}}, attempts=3, max_delay=2) == [1, 2, 2]

response = {"status": 429, "headers": {"Retry-After": "7"}}
original = copy.deepcopy(response)
assert mod.plan_retries(response, attempts=3) == [7, 14, 28]
assert response == original

future = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=11)
header_date = email.utils.format_datetime(future, usegmt=True)
planned = mod.plan_retries(
    {"status": 503, "headers": {"retry-after": header_date}},
    attempts=2,
    max_delay=20,
)
assert len(planned) == 2
assert 1 <= planned[0] <= 12
assert planned[1] == min(planned[0] * 2, 20)

assert mod.plan_retries(
    {"status": 408, "headers": {"Retry-After": "999"}},
    attempts=2,
    max_delay=30,
) == [30, 30]
