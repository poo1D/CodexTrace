import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from json_patch import apply_patch


class JsonPatchTest(unittest.TestCase):
    def test_add_replace_remove_without_mutating_input(self):
        document = {"name": "Ada", "tags": ["math"]}
        patched = apply_patch(document, [
            {"op": "add", "path": "/tags/1", "value": "code"},
            {"op": "replace", "path": "/name", "value": "Grace"},
            {"op": "remove", "path": "/tags/0"},
        ])
        self.assertEqual(patched, {"name": "Grace", "tags": ["code"]})
        self.assertEqual(document, {"name": "Ada", "tags": ["math"]})


if __name__ == "__main__":
    unittest.main()
