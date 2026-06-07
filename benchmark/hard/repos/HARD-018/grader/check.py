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
mod = importlib.import_module("frontmatter")

assert mod.parse_frontmatter("") == ({}, "")
assert mod.parse_frontmatter("plain body\n") == ({}, "plain body\n")

metadata, body = mod.parse_frontmatter("---\ntitle: A: B\ntags: one, two\n---\nBody")
assert metadata == {"title": "A: B", "tags": "one, two"}
assert body == "Body"

try:
    mod.parse_frontmatter("---\ntitle without colon\n---\n")
except mod.FrontmatterError as exc:
    message = str(exc).lower()
    assert "line 2" in message or "metadata" in message
else:
    raise AssertionError("metadata lines without ':' should raise FrontmatterError")

try:
    mod.parse_frontmatter("---\ntitle: Hello\n--\nBody")
except mod.FrontmatterError as exc:
    assert "closing" in str(exc).lower()
else:
    raise AssertionError("malformed closing delimiter should raise FrontmatterError")
