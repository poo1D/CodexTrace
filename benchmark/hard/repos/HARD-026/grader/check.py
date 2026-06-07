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
mod = importlib.import_module("rules_engine")

rules = [
    {"name": "legacy-catchall", "conditions": {}, "result": "legacy-review"},
    {"name": "low-risk", "conditions": {"type": "transfer"}, "result": "allow", "priority": 1},
    {"name": "high-risk", "conditions": {"type": "transfer", "amount": 9000}, "result": "block", "priority": 50},
]
assert mod.evaluate({"type": "transfer", "amount": 9000}, rules, default="manual") == "block"

tie_rules = [
    {"conditions": {"segment": "vip"}, "result": "first", "priority": 7},
    {"conditions": {"segment": "vip"}, "result": "second", "priority": 7},
]
assert mod.evaluate({"segment": "vip"}, tie_rules) == "first"

zero_priority_rules = [
    {"conditions": {"region": "EU"}, "result": "legacy-fallback"},
    {"conditions": {"region": "EU"}, "result": "explicit-zero", "priority": 0},
]
assert mod.evaluate({"region": "EU"}, zero_priority_rules) == "explicit-zero"

negative_priority_rules = [
    {"conditions": {"kind": "login"}, "result": "legacy-login"},
    {"conditions": {"kind": "login"}, "result": "priority-negative", "priority": -5},
]
assert mod.evaluate({"kind": "login"}, negative_priority_rules) == "priority-negative"

fallback_rules = [
    {"conditions": {"country": "US"}, "result": "legacy-us"},
    {"conditions": {"country": "CA"}, "result": "priority-ca", "priority": 20},
]
assert mod.evaluate({"country": "US"}, fallback_rules, default="manual") == "legacy-us"
assert mod.evaluate({"country": "MX"}, fallback_rules, default="manual") == "manual"

mutation_rules = [
    {"conditions": {"status": "new"}, "result": "legacy-new"},
    {"conditions": {"status": "new"}, "result": "priority-new", "priority": 3},
]
snapshot = [dict(rule) for rule in mutation_rules]
assert mod.evaluate({"status": "new"}, mutation_rules) == "priority-new"
assert mutation_rules == snapshot
