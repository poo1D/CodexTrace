You are Codex working on a coding benchmark task.

Task ID: HARD-040
Category: stateful_regression
Repository hint: python/ledger_reconciler

User request:
Fix the ledger reconciler so posting batches are atomic, duplicate event ids are ignored, reversal events negate the original event exactly once, currency mismatches raise LedgerError, and input events/accounts are not mutated. Preserve apply_events(accounts, events).

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
