You are Codex working on a coding benchmark task.

Task ID: HARD-027
Category: dependency_friction
Repository hint: typescript/date_formatter

User request:
Fix the date formatter so it no longer depends on external date libraries. It must format dates deterministically using the built-in runtime only, support UTC-based formatting with optional fixed timezone offsets, handle literals, and raise DateFormatError for invalid dates.

Success check:
npm test

Complete the task with your normal coding workflow.
