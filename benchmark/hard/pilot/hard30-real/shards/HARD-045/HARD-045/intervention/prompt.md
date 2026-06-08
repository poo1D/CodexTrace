You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-045
Category: stateful_regression
Repository hint: python/stream_window_join

User request:
Fix the streaming window joiner so out-of-order left/right events join within a time tolerance, watermarks evict only safely expired buffered events, duplicate event ids are ignored, late events are counted but not emitted, and snapshot() returns an isolated copy. Preserve WindowJoiner(tolerance_ms) with add_left, add_right, advance_watermark, and snapshot.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
