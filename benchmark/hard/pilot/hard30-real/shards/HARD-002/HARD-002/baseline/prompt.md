You are Codex working on a coding benchmark task.

Task ID: HARD-002
Category: bug_fix
Repository hint: python/csv_records

User request:
Fix the CSV reader so quoted commas, escaped double quotes, blank lines, and quoted newlines are parsed correctly without changing the public function.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
