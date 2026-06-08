You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-040
Category: stateful_regression
Repository hint: python/ledger_reconciler

User request:
Fix the ledger reconciler so posting batches are atomic, duplicate event ids are ignored, reversal events negate the original event exactly once, currency mismatches raise LedgerError, and input events/accounts are not mutated. Preserve apply_events(accounts, events).

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
