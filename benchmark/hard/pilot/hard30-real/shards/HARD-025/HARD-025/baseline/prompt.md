You are Codex working on a coding benchmark task.

Task ID: HARD-025
Category: ci_failure
Repository hint: python/typing_protocol

User request:
Fix the protocol typing CI failure so MemoryEventWriter structurally conforms to EventWriter and publish_events works with any protocol-compatible writer without changing the public API.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
