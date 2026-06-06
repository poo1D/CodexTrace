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
mod = importlib.import_module("rate_limiter")
limiter = mod.SlidingWindowLimiter(2, 10, allowlist={"vip"})
assert all(limiter.allow("vip", t) for t in range(5))
assert limiter.allow("user", 1)
assert limiter.allow("user", 2)
assert not limiter.allow("user", 3)
