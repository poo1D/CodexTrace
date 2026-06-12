import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from settings import resolve_settings


class SettingsTest(unittest.TestCase):
    def test_cli_wins_over_env(self):
        self.assertEqual(resolve_settings({}, env={"page_size": 10}, cli={"page_size": 5})["page_size"], 5)


if __name__ == "__main__":
    unittest.main()
