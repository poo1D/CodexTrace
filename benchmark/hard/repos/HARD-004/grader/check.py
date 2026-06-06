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
mod = importlib.import_module("toposort")
assert mod.topological_sort({"b": ["a"], "c": ["a"], "d": ["b", "c"]}) == ["a", "b", "c", "d"]
try:
    mod.topological_sort({"a": ["b"], "b": ["c"], "c": ["a"]})
except mod.CycleError as exc:
    text = " ".join(str(part) for part in exc.args)
    assert "a" in text and "b" in text and "c" in text
else:
    raise AssertionError("cycle should raise CycleError")
