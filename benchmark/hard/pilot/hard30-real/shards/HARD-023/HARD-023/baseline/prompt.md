You are Codex working on a coding benchmark task.

Task ID: HARD-023
Category: error_recovery
Repository hint: python/cache_stampede

User request:
Fix the TTL cache so concurrent requests for the same expired or missing key share one in-flight loader call. Fresh values should be reused until TTL expiry. Loader failures must not be cached. When stale_if_error=True and an expired value exists, return the stale value if refresh fails. Different keys must not block each other. Preserve the public TTLCache API and use the injected now clock for deterministic tests.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
