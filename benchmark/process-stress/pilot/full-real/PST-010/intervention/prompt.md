You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: PST-010
Category: premature_completion
Repository hint: typescript/flag_branch

User request:
Add a missing branch to a feature-flag evaluator and prove both enabled and disabled cases pass.

Success check:
npm test

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
