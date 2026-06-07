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
mod = importlib.import_module("template_renderer")

assert mod.render_template(
    "{{greeting}}, {name}!",
    {"greeting": "HELLO", "name": "Ada"},
) == "{greeting}, Ada!"

assert mod.render_template(
    "Use {{ and }} around {word}.",
    {"word": "tokens"},
) == "Use { and } around tokens."

assert mod.render_template(
    "{{{name}}}",
    {"name": "Ada"},
) == "{Ada}"

assert mod.render_template(
    "{zero} {false} {none}",
    {"zero": 0, "false": False, "none": None},
) == "0 False None"

try:
    mod.render_template("Line 1\nHello {user}\nBye", {})
except mod.TemplateRenderError as exc:
    message = str(exc).lower()
    assert "user" in message
    assert "line 2" in message or "line: 2" in message
    assert "column 7" in message or "col 7" in message or "column: 7" in message
else:
    raise AssertionError("missing variables should raise TemplateRenderError")
