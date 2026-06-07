# migration-runner

`run_migrations(store, migrations)` applies migration objects
to an in-memory store and returns the updated store.

Store shape:

```python
{
    "data": {},
    "applied": {"001_init": "checksum"},
}
```

Migration shape:

```python
{
    "id": "002_add_users",
    "checksum": "sha",
    "depends_on": ["001_init"],
    "apply": callable,
}
```

Requirements:

- Apply pending migrations in dependency order.
- Skip already-applied migration ids after validating checksums.
- Roll back all data and applied changes if any migration fails.
- Raise `MigrationError` for missing dependencies, cycles, and
  checksum drift.
