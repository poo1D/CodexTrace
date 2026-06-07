import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from migrator import run_migrations


class MigratorTest(unittest.TestCase):
    def test_applies_fixture_migrations(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "app.db"

            applied = run_migrations(db_path, root / "migrations")

            self.assertIn("001_init.sql", applied)
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute(
                    "SELECT id, name FROM users ORDER BY id"
                ).fetchall()
            self.assertEqual(rows, [(1, "Ada")])

    def test_dry_run_lists_migrations(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "app.db"

            pending = run_migrations(db_path, root / "migrations", dry_run=True)

            self.assertIn("001_init.sql", pending)
            self.assertIn("002_seed.sql", pending)


if __name__ == "__main__":
    unittest.main()
