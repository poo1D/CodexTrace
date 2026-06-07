import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from path_normalizer import normalize_path


class PathNormalizerTest(unittest.TestCase):
    def test_collapses_posix_separators_and_current_dir(self):
        self.assertEqual(normalize_path("docs//./guide.md"), "docs/guide.md")

    def test_resolves_relative_parent(self):
        self.assertEqual(normalize_path("docs/api/../index.md"), "docs/index.md")

    def test_empty_path_is_current_directory(self):
        self.assertEqual(normalize_path(""), ".")


if __name__ == "__main__":
    unittest.main()
