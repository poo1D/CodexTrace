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
mod = importlib.import_module("window_join")

joiner = mod.WindowJoiner(tolerance_ms=5)
assert joiner.add_right({"id": "r1", "time": 100, "value": "R"}) == []
emitted = joiner.add_left({"id": "l1", "time": 104, "value": "L"})
assert [(left["id"], right["id"]) for left, right in emitted] == [("l1", "r1")]

assert joiner.add_left({"id": "l1", "time": 104, "value": "L-duplicate"}) == []
assert joiner.add_right({"id": "r1", "time": 103, "value": "R-duplicate"}) == []

joiner = mod.WindowJoiner(tolerance_ms=10)
joiner.add_left({"id": "l-old", "time": 100, "value": "old"})
joiner.add_left({"id": "l-keep", "time": 111, "value": "keep"})
joiner.advance_watermark(105)
snap = joiner.snapshot()
assert [event["id"] for event in snap["left"]] == ["l-keep"]
assert joiner.add_right({"id": "r-keep", "time": 116, "value": "R"})
assert joiner.add_left({"id": "late", "time": 104, "value": "late"}) == []
assert joiner.snapshot()["late_count"] == 1

snapshot = joiner.snapshot()
snapshot["left"].append({"id": "mutated", "time": 999, "value": "x"})
assert all(event["id"] != "mutated" for event in joiner.snapshot()["left"])

joiner = mod.WindowJoiner(tolerance_ms=3)
assert joiner.add_left({"id": "l2", "time": 200, "value": "L"}) == []
assert joiner.add_right({"id": "r2", "time": 204, "value": "R"}) == []
assert joiner.add_right({"id": "r3", "time": 203, "value": "R3"})
