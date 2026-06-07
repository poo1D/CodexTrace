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
import os
import subprocess

run_visible_tests()

env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT / "src")
app = ROOT / "fixtures" / "app"
nested = app / "services" / "api"

def run_cli(cwd, *args):
    result = subprocess.run(
        [sys.executable, "-m", "env_manifest_resolver.cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(result.stdout)

root_output = run_cli(app, "manifest.json")
nested_output = run_cli(nested, "../../manifest.json")
assert nested_output == root_output

assert root_output["API_URL"] == "https://shared.example.test"
assert root_output["TIMEOUT"] == "5"
assert list(root_output.keys()) == ["API_URL", "FEATURE_FLAG", "REGION", "TIMEOUT"]

explicit_empty = run_cli(app, "manifest.json", "--set", "API_URL=")
assert explicit_empty["API_URL"] == ""

explicit_nested = run_cli(nested, "../../manifest.json", "--set", "FEATURE_FLAG=on")
assert explicit_nested["FEATURE_FLAG"] == "on"
assert explicit_nested["API_URL"] == "https://shared.example.test"
