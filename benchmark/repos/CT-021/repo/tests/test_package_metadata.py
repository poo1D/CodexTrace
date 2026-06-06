import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from package_metadata import package_name


class PackageMetadataTest(unittest.TestCase):
    def test_name(self):
        self.assertEqual(package_name(), "package-metadata-demo")


if __name__ == "__main__":
    unittest.main()
