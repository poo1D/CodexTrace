import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SnapshotManifestTest(unittest.TestCase):
    def test_builds_basic_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "manifest.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "manifest_cli",
                    "build-manifest",
                    "fixtures/project",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                env={"PYTHONPATH": str(ROOT / "src")},
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads(output.read_text())
            paths = {entry["path"] for entry in manifest["entries"]}
            self.assertIn("README.md", paths)
            self.assertIn("src/app.py", paths)


if __name__ == "__main__":
    unittest.main()
