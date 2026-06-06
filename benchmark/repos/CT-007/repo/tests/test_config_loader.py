import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config_loader import load_config


class ConfigLoaderTest(unittest.TestCase):
    def test_environment_override(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            json.dump({"port": 8000, "debug": False}, handle)
            path = handle.name
        self.assertEqual(load_config(path, {"APP_PORT": "9000"})["port"], 9000)


if __name__ == "__main__":
    unittest.main()
