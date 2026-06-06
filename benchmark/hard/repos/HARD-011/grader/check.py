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
mod = importlib.import_module("json_patch")
document = {"a/b": {"~key": ["x", "y"]}, "target": {}}
patched = mod.apply_patch(document, [
    {"op": "copy", "from": "/a~1b/~0key/1", "path": "/target/copied"},
    {"op": "move", "from": "/a~1b/~0key/0", "path": "/target/moved"},
    {"op": "add", "path": "/a~1b/~0key/-", "value": "z"},
])
assert patched == {"a/b": {"~key": ["y", "z"]}, "target": {"copied": "y", "moved": "x"}}
assert document == {"a/b": {"~key": ["x", "y"]}, "target": {}}
try:
    mod.apply_patch({"items": []}, [{"op": "remove", "path": "/items/0"}])
except mod.PatchError:
    pass
else:
    raise AssertionError("invalid remove path should raise PatchError")
