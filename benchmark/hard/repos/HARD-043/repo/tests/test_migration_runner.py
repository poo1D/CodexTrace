import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from migration_runner import run_migrations


class MigrationRunnerTest(unittest.TestCase):
    def test_applies_simple_migrations(self):
        store = {"data": {}, "applied": {}}
        migrations = [
            {
                "id": "001_init",
                "checksum": "a",
                "depends_on": [],
                "apply": lambda data: data.update({"users": []}),
            },
            {
                "id": "002_seed",
                "checksum": "b",
                "depends_on": ["001_init"],
                "apply": lambda data: data["users"].append("ada"),
            },
        ]

        result = run_migrations(store, migrations)

        self.assertEqual(result["data"]["users"], ["ada"])
        self.assertEqual(result["applied"], {"001_init": "a", "002_seed": "b"})

    def test_skips_applied_migration(self):
        store = {"data": {"users": ["ada"]}, "applied": {"001_init": "a"}}
        migrations = [
            {
                "id": "001_init",
                "checksum": "a",
                "depends_on": [],
                "apply": lambda data: data["users"].append("grace"),
            }
        ]

        result = run_migrations(store, migrations)

        self.assertEqual(result["data"]["users"], ["ada"])


if __name__ == "__main__":
    unittest.main()
