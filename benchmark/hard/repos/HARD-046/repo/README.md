# sqlite-migration-runner

`run_migrations(db_path, migrations_dir, dry_run=False)` applies
SQL migration files to a SQLite database.

Migration files are named with a numeric prefix, for example:

- `001_init.sql`
- `002_seed.sql`
- `010_add_status.sql`

Requirements:

- apply numbered migrations in numeric order
- apply each migration at most once
- store applied migration names and content checksums
- raise `MigrationError` if an applied migration file changes
- roll back a failed migration atomically
- make `dry_run=True` return pending migration names without
  creating or changing database state
