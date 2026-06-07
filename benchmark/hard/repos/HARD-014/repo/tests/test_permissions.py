import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from permissions import can_access


class PermissionTest(unittest.TestCase):
    def test_role_inherits_parent_allow(self):
        matrix = {
            "viewer": {"allow": ["read"]},
            "editor": {"inherits": ["viewer"], "allow": ["write"]},
        }
        self.assertTrue(can_access({"role": "editor"}, "read", matrix))
        self.assertTrue(can_access({"role": "editor"}, "write", matrix))


if __name__ == "__main__":
    unittest.main()
