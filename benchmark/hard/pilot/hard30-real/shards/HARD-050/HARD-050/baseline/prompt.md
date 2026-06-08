You are Codex working on a coding benchmark task.

Task ID: HARD-050
Category: multi_turn_change
Repository hint: python/config_overlay_resolver

User request:
Fix the config resolver so resolve_config(defaults, env=None, cli=None, schema=None) deep-merges defaults with environment and CLI overrides. Environment variables use APP_ plus double-underscore path separators, CLI keys use dotted paths, CLI overrides env, values are coerced using the schema, explicit false and zero overrides are preserved, unknown keys raise ConfigError, and inputs are not mutated. Use only the Python standard library.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
