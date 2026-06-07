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
mod = importlib.import_module("config_resolver")

defaults = {
    "server": {"host": "localhost", "port": 8000},
    "features": {"search": True, "beta": False},
    "limits": {"retries": 3, "ratio": 0.5},
    "tags": ["base"],
}
schema = {
    "server.host": str,
    "server.port": int,
    "features.search": bool,
    "features.beta": bool,
    "limits.retries": int,
    "limits.ratio": float,
    "tags": list,
}
env = {
    "APP_SERVER__PORT": "9000",
    "APP_FEATURES__SEARCH": "false",
    "APP_LIMITS__RATIO": "0.75",
    "IGNORED_VALUE": "x",
}
cli = {
    "features.beta": "true",
    "limits.retries": 0,
    "tags": "api,worker",
}
before_defaults = copy.deepcopy(defaults)
before_env = copy.deepcopy(env)
before_cli = copy.deepcopy(cli)

resolved = mod.resolve_config(defaults, env=env, cli=cli, schema=schema)

assert resolved == {
    "server": {"host": "localhost", "port": 9000},
    "features": {"search": False, "beta": True},
    "limits": {"retries": 0, "ratio": 0.75},
    "tags": ["api", "worker"],
}
assert defaults == before_defaults
assert env == before_env
assert cli == before_cli

override_false = mod.resolve_config(
    defaults,
    cli={"features.search": False, "server.port": 0},
    schema=schema,
)
assert override_false["features"]["search"] is False
assert override_false["server"]["port"] == 0

for bad_env, bad_cli in [
    ({"APP_SERVER__UNKNOWN": "x"}, {}),
    ({}, {"missing.path": "x"}),
]:
    try:
        mod.resolve_config(defaults, env=bad_env, cli=bad_cli, schema=schema)
    except mod.ConfigError as error:
        assert "unknown" in str(error).lower()
    else:
        raise AssertionError("unknown config path was accepted")

try:
    mod.resolve_config(defaults, cli={"server.port": "not-int"}, schema=schema)
except mod.ConfigError as error:
    assert "server.port" in str(error)
else:
    raise AssertionError("invalid typed override was accepted")
