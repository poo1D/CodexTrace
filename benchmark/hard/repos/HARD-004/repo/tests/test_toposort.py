import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from toposort import topological_sort


class ToposortTest(unittest.TestCase):
    def test_dependency_only_node_is_included_before_user(self):
        self.assertEqual(topological_sort({"app": ["core"]}), ["core", "app"])


if __name__ == "__main__":
    unittest.main()
