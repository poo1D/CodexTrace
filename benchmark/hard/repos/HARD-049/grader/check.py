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

run_visible_tests()
mod = importlib.import_module("sharder")

tests = [
    {"id": "test_checkout", "estimated_seconds": 8, "file": "checkout.py"},
    {"id": "test_auth", "estimated_seconds": 7, "file": "auth.py"},
    {"id": "test_billing", "estimated_seconds": 6, "file": "billing.py"},
    {"id": "test_cart", "estimated_seconds": 5, "file": "cart.py"},
]
before = copy.deepcopy(tests)

shards = mod.plan_shards(tests, 2)
assert tests == before
assert shards == [
    {"index": 0, "tests": ["test_checkout", "test_cart"], "estimated_seconds": 13},
    {"index": 1, "tests": ["test_auth", "test_billing"], "estimated_seconds": 13},
]

tie_tests = [
    {"id": "test_c", "estimated_seconds": 5},
    {"id": "test_a", "estimated_seconds": 5},
    {"id": "test_b", "estimated_seconds": 5},
]
tie_shards = mod.plan_shards(tie_tests, 2)
assert tie_shards == [
    {"index": 0, "tests": ["test_a", "test_c"], "estimated_seconds": 10},
    {"index": 1, "tests": ["test_b"], "estimated_seconds": 5},
]

quarantined = {"test_flaky"}
with_quarantine = [
    {"id": "test_fast", "estimated_seconds": 1},
    {"id": "test_flaky", "estimated_seconds": 100},
    {"id": "test_slow", "estimated_seconds": 9},
]
shards = mod.plan_shards(with_quarantine, 2, quarantined=quarantined)
assigned = [test_id for shard in shards for test_id in shard["tests"]]
assert assigned == ["test_slow", "test_fast"]
assert "test_flaky" not in assigned

empty = mod.plan_shards([{"id": "test_only", "estimated_seconds": 3}], 3)
assert len(empty) == 3
assert empty[2] == {"index": 2, "tests": [], "estimated_seconds": 0}

for bad_count in [0, -1]:
    try:
        mod.plan_shards([], bad_count)
    except mod.ShardError:
        pass
    else:
        raise AssertionError("invalid shard count was accepted")

try:
    mod.plan_shards([
        {"id": "test_dup", "estimated_seconds": 1},
        {"id": "test_dup", "estimated_seconds": 2},
    ], 2)
except mod.ShardError as error:
    assert "duplicate" in str(error).lower()
else:
    raise AssertionError("duplicate ids were accepted")
