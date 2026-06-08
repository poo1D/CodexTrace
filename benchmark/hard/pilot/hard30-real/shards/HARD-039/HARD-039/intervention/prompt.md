You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-039
Category: multi_turn_tool_debug
Repository hint: python/cli_report_writer

User request:
Fix the report CLI so --format json and --format text produce deterministic output from any current working directory, create parent directories for the output path, write atomically through a temporary sibling file, and leave existing output untouched when rendering fails. Preserve python3 -m report_writer.cli.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
