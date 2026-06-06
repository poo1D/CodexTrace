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
allocation = importlib.import_module("allocation")
assert allocation.allocate_cents(5, [1, 1, 1, 1]) == [2, 1, 1, 1]
assert allocation.allocate_cents(0, [5, 0, 2]) == [0, 0, 0]
assert allocation.allocate_cents(7, [0, 3, 3]) == [0, 4, 3]
try:
    allocation.allocate_cents(10, [1, -1])
except ValueError:
    pass
else:
    raise AssertionError("negative weights should raise ValueError")
