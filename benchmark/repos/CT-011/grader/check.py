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
test_source = (ROOT / "tests" / "test_email_validator.py").read_text(encoding="utf-8")
assert "+" in test_source, "missing plus-addressing regression test"
assert "EXAMPLE.COM" in test_source or "Example.COM" in test_source or "uppercase" in test_source.lower()
