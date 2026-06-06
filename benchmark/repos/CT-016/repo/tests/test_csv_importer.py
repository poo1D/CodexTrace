import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from csv_importer import import_admins, import_users


class CsvImporterTest(unittest.TestCase):
    def test_imports_users_and_admins(self):
        row = {"name": "Aubrey", "email": "a@example.com"}
        self.assertEqual(import_users([row])[0]["name"], "Aubrey")
        self.assertEqual(import_admins([row])[0]["role"], "admin")


if __name__ == "__main__":
    unittest.main()
