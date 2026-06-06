import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lint_target import normalize_name


class LintTargetTest(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_name("  Aubrey "), "aubrey")


if __name__ == "__main__":
    unittest.main()
