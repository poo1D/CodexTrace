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


import threading
import time
from concurrent.futures import ThreadPoolExecutor

run_visible_tests()
mod = importlib.import_module("cache_stampede")

now = [0.0]
cache = mod.TTLCache(now=lambda: now[0])
assert cache.get_or_set("profile", lambda: {"name": "Ada"}, ttl=5) == {"name": "Ada"}

now[0] = 10.0

def failing_refresh():
    raise RuntimeError("origin unavailable")

assert cache.get_or_set("profile", failing_refresh, ttl=5, stale_if_error=True) == {"name": "Ada"}

cold_calls = []

def failing_cold():
    cold_calls.append("fail")
    raise ValueError("temporary")

try:
    cache.get_or_set("cold", failing_cold, ttl=5, stale_if_error=True)
except ValueError:
    pass
else:
    raise AssertionError("cold load failure should propagate")

assert cache.get_or_set("cold", lambda: "recovered", ttl=5, stale_if_error=True) == "recovered"
assert cold_calls == ["fail"]

cache = mod.TTLCache(now=lambda: 50.0)
entered = threading.Event()
release = threading.Event()
calls = []
calls_lock = threading.Lock()

def failing_once():
    with calls_lock:
        calls.append("load")
    entered.set()
    release.wait(timeout=2)
    raise RuntimeError("boom")

with ThreadPoolExecutor(max_workers=4) as pool:
    futures = [pool.submit(cache.get_or_set, "same", failing_once, 10) for _ in range(4)]
    assert entered.wait(timeout=1)
    time.sleep(0.05)
    release.set()
    for future in futures:
        try:
            future.result(timeout=1)
        except RuntimeError as exc:
            assert "boom" in str(exc)
        else:
            raise AssertionError("all waiters should observe the load failure")

assert calls == ["load"], "same-key concurrent failure should use one loader call"
assert cache.get_or_set("same", lambda: "ok", ttl=10) == "ok"

cache = mod.TTLCache(now=lambda: 100.0)
slow_started = threading.Event()
slow_release = threading.Event()

def slow_loader():
    slow_started.set()
    slow_release.wait(timeout=2)
    return "slow"

with ThreadPoolExecutor(max_workers=2) as pool:
    slow_future = pool.submit(cache.get_or_set, "slow", slow_loader, 10)
    assert slow_started.wait(timeout=1)
    fast_future = pool.submit(cache.get_or_set, "fast", lambda: "fast", 10)
    assert fast_future.result(timeout=0.2) == "fast"
    slow_release.set()
    assert slow_future.result(timeout=1) == "slow"
