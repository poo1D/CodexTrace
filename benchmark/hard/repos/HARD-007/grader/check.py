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
mod = importlib.import_module("config_merge")
base = {"db": {"host": "local", "ports": [1]}, "debug": True, "keep": "yes"}
override = {"db": {"ports": [2, 3]}, "debug": None}
original_base = copy.deepcopy(base)
original_override = copy.deepcopy(override)
assert mod.merge_config(base, override) == {"db": {"host": "local", "ports": [2, 3]}, "keep": "yes"}
assert base == original_base
assert override == original_override
assert hasattr(mod, "deep_merge") or hasattr(mod, "_deep_merge")
