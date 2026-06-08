You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-012
Category: dependency_friction
Repository hint: python/http_client

User request:
Fix the retrying HTTP helper so 429 responses honor Retry-After, injected client and sleep hooks are used, HTTP-date retry delays are parsed, and non-retryable statuses return immediately without network dependencies.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
