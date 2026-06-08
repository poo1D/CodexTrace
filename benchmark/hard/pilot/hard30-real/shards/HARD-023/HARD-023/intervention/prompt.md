You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-023
Category: error_recovery
Repository hint: python/cache_stampede

User request:
Fix the TTL cache so concurrent requests for the same expired or missing key share one in-flight loader call. Fresh values should be reused until TTL expiry. Loader failures must not be cached. When stale_if_error=True and an expired value exists, return the stale value if refresh fails. Different keys must not block each other. Preserve the public TTLCache API and use the injected now clock for deterministic tests.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
