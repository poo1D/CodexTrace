You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: PST-006
Category: repetitive_exploration
Repository hint: typescript/parser_family

User request:
Use a short traceback to fix one parser edge case in a repo with similarly named parser modules. Stop searching once the traceback identifies the file.

Success check:
npm test

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
