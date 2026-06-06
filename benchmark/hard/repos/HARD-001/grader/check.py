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
intervals = importlib.import_module("intervals")
assert intervals.merge_intervals([(0, 1), (1, 2), (2, 2), (2, 3)]) == [(0, 1), (1, 2), (2, 2), (2, 3)]
assert intervals.merge_intervals([(4, 9), (1, 5), (2, 3), (9, 10)]) == [(1, 9), (9, 10)]
try:
    intervals.merge_intervals([(3, 1)])
except ValueError:
    pass
else:
    raise AssertionError("invalid interval should raise ValueError")
