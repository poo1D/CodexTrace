You are Codex working on a coding benchmark task.

Task ID: HARD-039
Category: multi_turn_tool_debug
Repository hint: python/cli_report_writer

User request:
Fix the report CLI so --format json and --format text produce deterministic output from any current working directory, create parent directories for the output path, write atomically through a temporary sibling file, and leave existing output untouched when rendering fails. Preserve python3 -m report_writer.cli.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
