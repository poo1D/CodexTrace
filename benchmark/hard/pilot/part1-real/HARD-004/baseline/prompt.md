You are Codex working on a coding benchmark task.

Task ID: HARD-004
Category: error_localization
Repository hint: python/toposort

User request:
Fix topological sorting so dependency-only nodes are included, output is stable by first appearance, and cycles raise CycleError with the cycle path.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
