You are Codex working on a coding benchmark task.

Task ID: HARD-031
Category: multi_turn_tool_debug
Repository hint: python/env_manifest_resolver

User request:
Fix the environment manifest resolver so the CLI produces the same resolved JSON whether it is run from the repo root or a nested directory. Preserve documented precedence: defaults < .env < .env.local < explicit --set KEY=VALUE. Empty values in .env.local should not erase existing values unless passed explicitly with --set.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
