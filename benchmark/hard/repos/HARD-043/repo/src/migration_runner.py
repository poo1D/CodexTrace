class MigrationError(Exception):
    pass


def run_migrations(store, migrations):
    data = store.setdefault("data", {})
    applied = store.setdefault("applied", {})
    for migration in migrations:
        migration_id = migration["id"]
        if migration_id in applied:
            continue
        applied[migration_id] = migration.get("checksum", "")
        migration["apply"](data)
    return store
