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


import json
import tempfile
run_visible_tests()
loader = importlib.import_module("config_loader")
with tempfile.NamedTemporaryFile("w", delete=False) as handle:
    json.dump({"port": 8000, "debug": False, "name": "local"}, handle)
    path = handle.name
loaded = loader.load_config(path, {"APP_PORT": "7000", "APP_DEBUG": "true", "APP_NAME": "prod"})
assert loaded == {"port": 7000, "debug": True, "name": "prod"}
