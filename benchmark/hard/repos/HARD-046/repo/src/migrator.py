import sqlite3
from pathlib import Path


class MigrationError(Exception):
    pass


def run_migrations(db_path, migrations_dir, dry_run=False):
    files = sorted(Path(migrations_dir).glob("*.sql"))
    names = [path.name for path in files]
    if dry_run:
        return names

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations "
            "(name TEXT PRIMARY KEY)"
        )
        applied = {
            row[0]
            for row in conn.execute("SELECT name FROM schema_migrations")
        }
        for path in files:
            if path.name in applied:
                continue
            conn.executescript(path.read_text(encoding="utf-8"))
            conn.execute(
                "INSERT INTO schema_migrations(name) VALUES (?)",
                (path.name,),
            )
        conn.commit()
    finally:
        conn.close()
    return names
