You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-043
Category: data_migration
Repository hint: python/migration_runner

User request:
Fix the migration runner so it applies pending migrations in dependency order, skips already-applied migration ids, validates recorded checksums, rolls back all changes on failure, and preserves run_migrations(store, migrations). Raise MigrationError with useful diagnostics for missing dependencies, dependency cycles, and checksum drift.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
