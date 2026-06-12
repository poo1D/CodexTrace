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
import json
import tempfile
mod = importlib.import_module("exporter")
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "a" / "b" / "out.json"
    mod.export_json(path, {"items": [1, 2]})
    assert json.loads(path.read_text(encoding="utf-8")) == {"items": [1, 2]}
