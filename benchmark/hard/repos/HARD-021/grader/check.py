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
mod = importlib.import_module("currency")

assert mod.parse_cents("(1,234.50)") == -123450
assert mod.parse_cents("($19.99)") == -1999
assert mod.parse_cents("USD 2,500.05") == 250005
assert mod.parse_cents("EUR -0.99") == -99
assert mod.parse_cents("0.10") == 10
assert mod.parse_cents("42") == 4200

malformed = ["1,23", "1.234,56", "$12.345", "(12.00", "USD"]
for value in malformed:
    try:
        mod.parse_cents(value)
    except mod.CurrencyParseError:
        pass
    else:
        raise AssertionError(f"malformed amount should fail: {value!r}")
