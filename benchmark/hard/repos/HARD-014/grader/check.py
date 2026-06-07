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
mod = importlib.import_module("permissions")
matrix = {
    "guest": {"allow": ["read"], "deny": ["delete"]},
    "member": {"inherits": ["guest"], "allow": ["comment"]},
    "moderator": {"inherits": ["member"], "allow": ["delete"], "deny": ["billing"]},
    "admin": {"inherits": ["moderator"], "allow": ["billing"]},
}
original = copy.deepcopy(matrix)
assert mod.can_access({"role": "admin"}, "read", matrix)
assert mod.can_access({"role": "admin"}, "comment", matrix)
assert not mod.can_access({"role": "admin"}, "delete", matrix), "deny inherited from guest overrides later allow"
assert not mod.can_access({"role": "admin"}, "billing", matrix), "moderator deny overrides admin allow"
assert mod.can_access({"role": "member", "allow": ["billing"]}, "billing", matrix), "user allow wins last"
assert not mod.can_access({"role": "admin", "deny": ["read"]}, "read", matrix), "user deny wins last"
assert matrix == original
assert hasattr(mod, "resolve_permissions") or hasattr(mod, "_resolve_permissions")
