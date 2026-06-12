import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cli_args import CliArgError, parse_args


class CliArgsTest(unittest.TestCase):
    def test_rejects_missing_limit_value(self):
        with self.assertRaises(CliArgError):
            parse_args(["--limit"])


if __name__ == "__main__":
    unittest.main()
