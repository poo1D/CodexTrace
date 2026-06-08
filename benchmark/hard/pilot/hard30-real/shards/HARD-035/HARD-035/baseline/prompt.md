You are Codex working on a coding benchmark task.

Task ID: HARD-035
Category: dependency_friction
Repository hint: python/retry_policy

User request:
Fix the HTTP retry policy so it preserves the existing exponential backoff behavior while respecting retryable status codes, Retry-After headers, maximum delay caps, and input immutability. Use only the Python standard library.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
