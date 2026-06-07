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
mod = importlib.import_module("sliding_limiter")

limiter = mod.SlidingLimiter(limit=2, window_seconds=10)
assert limiter.allow("ada", now=100.0) is True
assert limiter.allow("ada", now=109.9) is True
assert limiter.allow("ada", now=110.0) is True
assert limiter.allow("ada", now=110.1) is False

limiter = mod.SlidingLimiter(limit=1, window_seconds=5)
assert limiter.allow("ada", now=10.0) is True
assert limiter.allow("grace", now=10.1) is True
assert limiter.allow("ada", now=10.2) is False
assert limiter.allow("grace", now=10.3) is False

limiter = mod.SlidingLimiter(limit=2, window_seconds=10)
assert limiter.allow("ada", now=50.0) is True
assert limiter.allow("ada", now=51.0) is True
assert limiter.allow("ada", now=51.5) is False
assert limiter.allow("ada", now=60.0) is True
assert limiter.allow("ada", now=60.1) is False

calls = []
times = iter([1.0, 2.0, 12.1])

def clock():
    calls.append("tick")
    return next(times)

limiter = mod.SlidingLimiter(limit=2, window_seconds=10, clock=clock)
assert limiter.allow("linus") is True
assert limiter.allow("linus") is True
assert limiter.allow("linus") is True
assert calls == ["tick", "tick", "tick"]

limiter = mod.SlidingLimiter(limit=1, window_seconds=1)
assert limiter.allow("ada", now=0.0) is True
assert limiter.allow("ada", now=1_000.0) is True
state = getattr(limiter, "_events", None)
if state is not None:
    assert len(state.get("ada", [])) <= 1
