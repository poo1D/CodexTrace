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


import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

run_visible_tests()

root = Path.cwd()
env = os.environ.copy()
env["PYTHONPATH"] = str(root / "src")

def run_cli(cwd, *args):
    return subprocess.run(
        [sys.executable, "-m", "report_writer.cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    nested_output = tmp_path / "nested" / "reports" / "summary.json"
    result = run_cli(
        root / "src",
        "--input", "fixtures/report.json",
        "--output", str(nested_output),
        "--format", "json",
    )
    assert result.returncode == 0, result.stderr
    text = nested_output.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert json.loads(text)["title"] == "Trace Summary"
    assert text.index('"metrics"') < text.index('"sections"') < text.index('"title"')

    text_output = tmp_path / "out" / "summary.txt"
    result = run_cli(
        root / "fixtures",
        "--input", "fixtures/report.json",
        "--output", str(text_output),
        "--format", "text",
    )
    assert result.returncode == 0, result.stderr
    rendered = text_output.read_text(encoding="utf-8").splitlines()
    assert rendered[:5] == [
        "Trace Summary",
        "",
        "Overview",
        "Agents completed most visible checks.",
        "",
    ]
    assert rendered[-2:] == ["token_usage: 15200", "verification_rate: 0.75"]

    bad_input = tmp_path / "bad.json"
    bad_input.write_text('{"title": "RAISE"}', encoding="utf-8")
    existing = tmp_path / "existing" / "report.txt"
    existing.parent.mkdir()
    existing.write_text("keep me\n", encoding="utf-8")
    result = run_cli(
        root,
        "--input", str(bad_input),
        "--output", str(existing),
        "--format", "text",
    )
    assert result.returncode != 0
    assert existing.read_text(encoding="utf-8") == "keep me\n"
    assert not list(existing.parent.glob("*.tmp"))
