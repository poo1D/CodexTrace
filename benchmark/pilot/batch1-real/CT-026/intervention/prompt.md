You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: CT-026
Category: error_localization
Repository hint: python/json_reader

User request:
Use the traceback to identify and fix a JSON decode edge case.

Success check:
python3 ../grader/check.py

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
