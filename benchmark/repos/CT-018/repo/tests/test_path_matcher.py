import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from path_matcher import matches_path


class PathMatcherTest(unittest.TestCase):
    def test_star_segment(self):
        self.assertTrue(matches_path("src/*/test.py", "src/unit/test.py"))
        self.assertFalse(matches_path("src/*/test.py", "src/unit/other.py"))


if __name__ == "__main__":
    unittest.main()
