import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config_resolver import resolve_config


class ConfigResolverTest(unittest.TestCase):
    def test_returns_defaults_when_no_overrides(self):
        defaults = {"host": "localhost", "mode": "dev"}

        resolved = resolve_config(defaults)

        self.assertEqual(resolved, defaults)
        self.assertIsNot(resolved, defaults)

    def test_cli_overrides_top_level_value(self):
        defaults = {"host": "localhost", "mode": "dev"}

        resolved = resolve_config(defaults, cli={"host": "0.0.0.0"})

        self.assertEqual(resolved["host"], "0.0.0.0")
        self.assertEqual(resolved["mode"], "dev")

    def test_app_env_overrides_top_level_value(self):
        defaults = {"host": "localhost"}

        resolved = resolve_config(defaults, env={"APP_HOST": "example.test"})

        self.assertEqual(resolved["host"], "example.test")


if __name__ == "__main__":
    unittest.main()
