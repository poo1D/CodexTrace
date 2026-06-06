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
date_utils = importlib.import_module("date_utils")
parsed = date_utils.parse_iso_datetime("2026-01-02T03:04:05Z")
assert parsed.utcoffset().total_seconds() == 0
assert date_utils.parse_iso_datetime("2026-01-02T03:04:05+02:00").utcoffset().total_seconds() == 7200
