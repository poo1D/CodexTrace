import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config_merge import merge_config


class ConfigMergeTest(unittest.TestCase):
    def test_deep_dict_merge(self):
        self.assertEqual(
            merge_config({"db": {"host": "local", "port": 1}}, {"db": {"port": 2}}),
            {"db": {"host": "local", "port": 2}},
        )


if __name__ == "__main__":
    unittest.main()
