import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicCliTest(unittest.TestCase):
    def run_cli(self, *args):
        env = {"PYTHONPATH": str(ROOT / "src")}
        return subprocess.run(
            [sys.executable, "-m", "report_writer.cli", *args],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_writes_json_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            result = self.run_cli(
                "--input", "fixtures/report.json",
                "--output", str(output),
                "--format", "json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text()), json.loads((ROOT / "fixtures/report.json").read_text()))

    def test_writes_text_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.txt"
            result = self.run_cli(
                "--input", "fixtures/report.json",
                "--output", str(output),
                "--format", "text",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Trace Summary", output.read_text())
            self.assertIn("Metrics", output.read_text())


if __name__ == "__main__":
    unittest.main()
