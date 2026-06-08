You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-032
Category: stateful_regression
Repository hint: typescript/undoable_queue

User request:
Fix the undoable queue so undo() and redo() preserve item metadata and queue ordering across enqueue, dequeue, and clear operations. Do not change the public API or test runner configuration.

Success check:
npm test

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
