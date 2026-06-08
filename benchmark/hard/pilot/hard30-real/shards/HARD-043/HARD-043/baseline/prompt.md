You are Codex working on a coding benchmark task.

Task ID: HARD-043
Category: data_migration
Repository hint: python/migration_runner

User request:
Fix the migration runner so it applies pending migrations in dependency order, skips already-applied migration ids, validates recorded checksums, rolls back all changes on failure, and preserves run_migrations(store, migrations). Raise MigrationError with useful diagnostics for missing dependencies, dependency cycles, and checksum drift.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
