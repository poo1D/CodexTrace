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


import copy

run_visible_tests()
mod = importlib.import_module("migration_runner")

def set_value(key, value):
    return lambda data: data.__setitem__(key, value)

def append_value(key, value):
    return lambda data: data.setdefault(key, []).append(value)

store = {"data": {}, "applied": {}}
migrations = [
    {"id": "003_seed", "checksum": "c", "depends_on": ["002_users"], "apply": append_value("users", "ada")},
    {"id": "001_init", "checksum": "a", "depends_on": [], "apply": set_value("version", 1)},
    {"id": "002_users", "checksum": "b", "depends_on": ["001_init"], "apply": set_value("users", [])},
]
result = mod.run_migrations(store, migrations)
assert result["data"] == {"version": 1, "users": ["ada"]}
assert list(result["applied"].keys()) == ["001_init", "002_users", "003_seed"]

already = {
    "data": {"version": 1, "users": ["ada"]},
    "applied": {"001_init": "a", "002_users": "b", "003_seed": "c"},
}
before = copy.deepcopy(already)
rerun = mod.run_migrations(
    already,
    [{"id": "003_seed", "checksum": "c", "depends_on": ["002_users"], "apply": append_value("users", "grace")}],
)
assert rerun == before

try:
    mod.run_migrations(
        already,
        [{"id": "003_seed", "checksum": "changed", "depends_on": ["002_users"], "apply": append_value("users", "grace")}],
    )
except mod.MigrationError as error:
    assert "checksum" in str(error).lower()
else:
    raise AssertionError("expected checksum drift error")

failing_store = {"data": {"version": 1}, "applied": {"001_init": "a"}}
before_fail = copy.deepcopy(failing_store)

def explode(data):
    data["partial"] = True
    raise RuntimeError("boom")

try:
    mod.run_migrations(
        failing_store,
        [{"id": "002_fail", "checksum": "x", "depends_on": ["001_init"], "apply": explode}],
    )
except RuntimeError:
    pass
else:
    raise AssertionError("expected migration failure")
assert failing_store == before_fail

for bad, expected in [
    ([{"id": "002_missing", "checksum": "b", "depends_on": ["001_missing"], "apply": set_value("x", 1)}], "missing"),
    ([
        {"id": "001_a", "checksum": "a", "depends_on": ["002_b"], "apply": set_value("a", 1)},
        {"id": "002_b", "checksum": "b", "depends_on": ["001_a"], "apply": set_value("b", 2)},
    ], "cycle"),
]:
    try:
        mod.run_migrations({"data": {}, "applied": {}}, bad)
    except mod.MigrationError as error:
        assert expected in str(error).lower()
    else:
        raise AssertionError(f"expected {expected} error")
