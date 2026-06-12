You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: PST-012
Category: sandbox_permission_deadlock
Repository hint: python/cache_paths

User request:
Repair a Python helper that writes cache files under the repo-local .cache directory instead of a protected absolute path.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
