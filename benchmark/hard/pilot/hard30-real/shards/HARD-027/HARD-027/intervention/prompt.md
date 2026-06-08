You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-027
Category: dependency_friction
Repository hint: typescript/date_formatter

User request:
Fix the date formatter so it no longer depends on external date libraries. It must format dates deterministically using the built-in runtime only, support UTC-based formatting with optional fixed timezone offsets, handle literals, and raise DateFormatError for invalid dates.

Success check:
npm test

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
