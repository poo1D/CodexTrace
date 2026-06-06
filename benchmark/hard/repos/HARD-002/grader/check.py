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
mod = importlib.import_module("csv_records")
text = "name,note\nAda,\"quote \"\"inside\"\"\"\n\nGrace,\"line one\nline two\""
assert mod.parse_records(text) == [
    ["name", "note"],
    ["Ada", 'quote "inside"'],
    ["Grace", "line one\nline two"],
]
