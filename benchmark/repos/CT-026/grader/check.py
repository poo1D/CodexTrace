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


import tempfile
run_visible_tests()
reader = importlib.import_module("json_reader")
with tempfile.NamedTemporaryFile("w", delete=False) as handle:
    handle.write("   ")
    empty_path = handle.name
assert reader.read_json(empty_path) == {}
with tempfile.NamedTemporaryFile("w", delete=False) as handle:
    handle.write('{"ok": true}')
    data_path = handle.name
assert reader.read_json(data_path) == {"ok": True}
