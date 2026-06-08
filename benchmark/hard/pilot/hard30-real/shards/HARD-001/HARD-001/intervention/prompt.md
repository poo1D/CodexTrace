You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-001
Category: bug_fix
Repository hint: python/interval_merge

User request:
Fix interval merging for half-open intervals: overlapping intervals merge, touching intervals stay separate, invalid intervals raise ValueError, and output remains sorted.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
