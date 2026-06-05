You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: SM-002
Category: feature
Repository hint: python/text_stats

User request:
Implement word_frequency so it lowercases words and ignores punctuation. Keep the return type as dict[str, int].

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
