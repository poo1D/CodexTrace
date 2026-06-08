You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-031
Category: multi_turn_tool_debug
Repository hint: python/env_manifest_resolver

User request:
Fix the environment manifest resolver so the CLI produces the same resolved JSON whether it is run from the repo root or a nested directory. Preserve documented precedence: defaults < .env < .env.local < explicit --set KEY=VALUE. Empty values in .env.local should not erase existing values unless passed explicitly with --set.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
