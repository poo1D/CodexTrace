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


from datetime import datetime, timezone
from zoneinfo import ZoneInfo

run_visible_tests()
mod = importlib.import_module("time_window")

ny = ZoneInfo("America/New_York")
utc = timezone.utc

before_fallback = (
    datetime(2024, 11, 3, 1, 15, tzinfo=ny, fold=0),
    datetime(2024, 11, 3, 1, 45, tzinfo=ny, fold=0),
)
after_fallback = (
    datetime(2024, 11, 3, 1, 30, tzinfo=ny, fold=1),
    datetime(2024, 11, 3, 2, 0, tzinfo=ny, fold=1),
)
assert not mod.overlaps(before_fallback, after_fallback), "folded DST windows must compare by absolute time"

same_instant_left = (
    datetime(2026, 5, 1, 12, 0, tzinfo=utc),
    datetime(2026, 5, 1, 13, 0, tzinfo=utc),
)
same_instant_right = (
    datetime(2026, 5, 1, 8, 30, tzinfo=ZoneInfo("America/New_York")),
    datetime(2026, 5, 1, 9, 30, tzinfo=ZoneInfo("America/New_York")),
)
assert mod.overlaps(same_instant_left, same_instant_right)

try:
    mod.overlaps(
        (datetime(2026, 1, 1, 10, 0), datetime(2026, 1, 1, 10, 0)),
        (datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 11, 0)),
    )
except ValueError:
    pass
else:
    raise AssertionError("empty windows should raise ValueError")

try:
    mod.overlaps(
        (datetime(2026, 1, 1, 11, 0), datetime(2026, 1, 1, 10, 0)),
        (datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 12, 0)),
    )
except ValueError:
    pass
else:
    raise AssertionError("inverted windows should raise ValueError")
