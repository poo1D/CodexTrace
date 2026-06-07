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
import hashlib

run_visible_tests()
mod = importlib.import_module("feature_flags")

config = {
    "default": False,
    "flags": {
        "search_v2": {
            "enabled": True,
            "rollout": 25,
            "allow_users": ["ada"],
            "deny_users": ["mallory"],
        },
        "checkout_v2": {
            "rollout": 0,
            "allow_users": ["grace"],
        },
        "feed_v2": {
            "rollout": 100,
            "deny_users": ["linus"],
        },
    },
}
original = copy.deepcopy(config)

assert mod.evaluate_flag(config, "search_v2", {"id": "ada"}) is True
assert mod.evaluate_flag(config, "search_v2", {"id": "mallory"}) is False
assert mod.evaluate_flag(config, "checkout_v2", {"id": "grace"}) is True
assert mod.evaluate_flag(config, "checkout_v2", {"id": "random"}) is False
assert mod.evaluate_flag(config, "feed_v2", {"id": "linus"}) is False
assert mod.evaluate_flag(config, "feed_v2", {"id": "anyone"}) is True

def bucket(flag_name, user_id):
    digest = hashlib.sha256(f"{flag_name}:{user_id}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100

users = [
    {"id": "user-001"},
    {"id": "user-017"},
    {"id": "user-042"},
    {"id": "user-099"},
]
for user in users:
    expected = bucket("search_v2", user["id"]) < 25
    assert mod.evaluate_flag(config, "search_v2", user) is expected

assert mod.evaluate_flag(config, "missing", {"id": "ada"}) is False
assert config == original

user = {"id": "ada", "groups": ["staff"]}
before_user = copy.deepcopy(user)
mod.evaluate_flag(config, "search_v2", user)
assert user == before_user
