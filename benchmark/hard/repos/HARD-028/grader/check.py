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
mod = importlib.import_module("path_normalizer")

assert mod.normalize_path(r"logs\\2026\\..\\latest\\run.txt") == "logs/latest/run.txt"
assert mod.normalize_path(r"C:\\Users\\Ada\\..\\Grace\\file.txt") == "C:/Users/Grace/file.txt"
assert mod.normalize_path("C:/Users/./Ada/../Grace") == "C:/Users/Grace"

assert mod.normalize_path("../src/./../README.md") == "../README.md"
assert mod.normalize_path("a/../../b") == "../b"
assert mod.normalize_path("././") == "."

assert mod.normalize_path("/var//log/../tmp/") == "/var/tmp"
assert mod.normalize_path("/../etc") == "/etc"
assert mod.normalize_path("/") == "/"

assert mod.normalize_path(r"C:\\..\\Windows") == "C:/Windows"
assert mod.normalize_path(r"\\\\server\\share\\folder\\..\\file.txt") == "//server/share/file.txt"
assert mod.normalize_path(r"\\\\server\\share\\..\\other") == "//server/share/other"
