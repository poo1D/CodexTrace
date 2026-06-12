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
mod = importlib.import_module("cli_args")
assert mod.parse_args(["--limit", "3", "--verbose"]) == {"limit": 3, "verbose": True}
for argv in (["--limit", "0"], ["--limit", "-1"], ["--unknown"]):
    try:
        mod.parse_args(argv)
    except mod.CliArgError:
        pass
    else:
        raise AssertionError(f"{argv!r} should fail")
