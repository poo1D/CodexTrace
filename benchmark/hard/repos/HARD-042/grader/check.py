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


import hashlib
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
        [sys.executable, "-m", "manifest_cli", "build-manifest", *args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

def load_manifest(path):
    return json.loads(path.read_text(encoding="utf-8"))

with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    output_a = tmp_path / "a" / "manifest.json"
    output_a.parent.mkdir()
    result = run_cli(
        root,
        "fixtures/project",
        "--output",
        str(output_a),
    )
    assert result.returncode == 0, result.stderr
    manifest_a = load_manifest(output_a)

    output_b = tmp_path / "b" / "manifest.json"
    output_b.parent.mkdir()
    result = run_cli(
        root / "fixtures",
        "fixtures/project",
        "--output",
        str(output_b),
    )
    assert result.returncode == 0, result.stderr
    assert load_manifest(output_b) == manifest_a

    entries = manifest_a["entries"]
    paths = [entry["path"] for entry in entries]
    assert paths == sorted(paths)
    assert all("\\" not in path for path in paths)
    assert "src/data.tmp" not in paths
    assert "build/output.txt" not in paths
    assert "empty" not in paths

    by_path = {entry["path"]: entry for entry in entries}
    expected_hash = hashlib.sha256((root / "fixtures/project/src/app.py").read_bytes()).hexdigest()
    assert by_path["src/app.py"]["sha256"] == expected_hash
    assert "size" not in by_path["src/app.py"]

    output_c = tmp_path / "c" / "manifest.json"
    output_c.parent.mkdir()
    result = run_cli(
        root,
        "fixtures/project",
        "--output",
        str(output_c),
        "--include-empty-dirs",
    )
    assert result.returncode == 0, result.stderr
    paths_with_dirs = [entry["path"] for entry in load_manifest(output_c)["entries"]]
    assert "empty" in paths_with_dirs
