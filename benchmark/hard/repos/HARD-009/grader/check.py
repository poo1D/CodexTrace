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
mod = importlib.import_module("booking_policy")
ranges = [("2026-07-01", "2026-07-10"), ("2026-12-24", "2026-12-31")]
assert not mod.can_book({"role": "member"}, "2026-12-25", 4, ranges)
assert mod.can_book({"role": "admin"}, "2026-12-25", 4, ranges)
assert not mod.can_book({"role": "admin"}, "2026-12-25", 0, ranges)
assert mod.can_book({"role": "member"}, "2026-07-10", 1, ranges), "ranges are end-exclusive"
