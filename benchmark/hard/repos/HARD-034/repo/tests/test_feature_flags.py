import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from feature_flags import evaluate_flag


class FeatureFlagsTest(unittest.TestCase):
    def test_enabled_flag_returns_true(self):
        config = {"flags": {"new_nav": {"enabled": True}}}

        self.assertTrue(evaluate_flag(config, "new_nav", {"id": "ada"}))

    def test_disabled_flag_returns_false(self):
        config = {"flags": {"new_nav": {"enabled": False}}}

        self.assertFalse(evaluate_flag(config, "new_nav", {"id": "ada"}))

    def test_missing_flag_uses_default(self):
        config = {"default": True, "flags": {}}

        self.assertTrue(evaluate_flag(config, "missing", {"id": "ada"}))


if __name__ == "__main__":
    unittest.main()
