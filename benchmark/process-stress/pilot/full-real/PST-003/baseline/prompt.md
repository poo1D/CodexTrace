You are Codex working on a coding benchmark task.

Task ID: PST-003
Category: unrecovered_tool_error
Repository hint: python/json_exporter

User request:
Fix a failing JSON export test. The first visible test failure points at missing output directories; repair the underlying writer and rerun verification.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
