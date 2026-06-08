You are Codex working on a coding benchmark task.

Task ID: HARD-001
Category: bug_fix
Repository hint: python/interval_merge

User request:
Fix interval merging for half-open intervals: overlapping intervals merge, touching intervals stay separate, invalid intervals raise ValueError, and output remains sorted.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
