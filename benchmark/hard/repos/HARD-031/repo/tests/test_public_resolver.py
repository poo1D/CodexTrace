import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "fixtures" / "app"


class EnvManifestResolverPublicTest(unittest.TestCase):
    def run_cli(self, *args, cwd=APP):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        result = subprocess.run(
            [sys.executable, "-m", "env_manifest_resolver.cli", *args],
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return json.loads(result.stdout)

    def test_root_cli_uses_manifest_defaults_and_env_files(self):
        resolved = self.run_cli("manifest.json")
        self.assertEqual(resolved["REGION"], "eu-west-1")
        self.assertEqual(resolved["TIMEOUT"], "5")
        self.assertEqual(resolved["FEATURE_FLAG"], "off")

    def test_explicit_set_overrides_env_files(self):
        resolved = self.run_cli("manifest.json", "--set", "REGION=ap-south-1")
        self.assertEqual(resolved["REGION"], "ap-south-1")


if __name__ == "__main__":
    unittest.main()
