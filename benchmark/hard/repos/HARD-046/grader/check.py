import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src"))


def run_visible_tests():
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(result.returncode)


import shutil
import sqlite3
import tempfile
from pathlib import Path

run_visible_tests()
mod = importlib.import_module("migrator")

root = Path.cwd()
source_migrations = root / "migrations"

with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    migrations = tmp_path / "migrations"
    shutil.copytree(source_migrations, migrations)
    db_path = tmp_path / "app.db"

    applied = mod.run_migrations(db_path, migrations)
    assert applied == ["001_init.sql", "002_seed.sql", "010_add_status.sql"]

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, name, status FROM users ORDER BY id"
        ).fetchall()
        migration_rows = conn.execute(
            "SELECT name, checksum FROM schema_migrations ORDER BY name"
        ).fetchall()
    assert rows == [(1, "Ada", "active")]
    assert [row[0] for row in migration_rows] == applied
    assert all(row[1] for row in migration_rows)

    again = mod.run_migrations(db_path, migrations)
    assert again == []
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        migration_count = conn.execute(
            "SELECT COUNT(*) FROM schema_migrations"
        ).fetchone()[0]
    assert count == 1
    assert migration_count == 3

    (migrations / "002_seed.sql").write_text(
        "INSERT INTO users (id, name) VALUES (2, 'Grace');\n",
        encoding="utf-8",
    )
    try:
        mod.run_migrations(db_path, migrations)
    except mod.MigrationError as error:
        assert "checksum" in str(error).lower()
    else:
        raise AssertionError("changed applied migration did not fail")

with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "001_init.sql").write_text(
        "CREATE TABLE ok_table (id INTEGER PRIMARY KEY);\n",
        encoding="utf-8",
    )
    (migrations / "002_bad.sql").write_text(
        "CREATE TABLE partial_table (id INTEGER);\n"
        "INSERT INTO partial_table VALUES (1);\n"
        "INSERT INTO missing_table VALUES (1);\n",
        encoding="utf-8",
    )
    db_path = tmp_path / "bad.db"

    try:
        mod.run_migrations(db_path, migrations)
    except Exception:
        pass
    else:
        raise AssertionError("bad migration unexpectedly succeeded")

    with sqlite3.connect(db_path) as conn:
        names = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        recorded = []
        if "schema_migrations" in names:
            recorded = conn.execute(
                "SELECT name FROM schema_migrations"
            ).fetchall()
    assert "partial_table" not in names
    assert ("002_bad.sql",) not in recorded

with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    migrations = tmp_path / "migrations"
    shutil.copytree(source_migrations, migrations)
    db_path = tmp_path / "dry.db"

    pending = mod.run_migrations(db_path, migrations, dry_run=True)
    assert pending == ["001_init.sql", "002_seed.sql", "010_add_status.sql"]
    with sqlite3.connect(db_path) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    assert tables == []
