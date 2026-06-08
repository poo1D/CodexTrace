You are Codex working on a coding benchmark task.

Task ID: HARD-012
Category: dependency_friction
Repository hint: python/http_client

User request:
Fix the retrying HTTP helper so 429 responses honor Retry-After, injected client and sleep hooks are used, HTTP-date retry delays are parsed, and non-retryable statuses return immediately without network dependencies.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
