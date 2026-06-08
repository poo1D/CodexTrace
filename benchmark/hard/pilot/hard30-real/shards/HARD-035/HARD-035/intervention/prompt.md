You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-035
Category: dependency_friction
Repository hint: python/retry_policy

User request:
Fix the HTTP retry policy so it preserves the existing exponential backoff behavior while respecting retryable status codes, Retry-After headers, maximum delay caps, and input immutability. Use only the Python standard library.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
