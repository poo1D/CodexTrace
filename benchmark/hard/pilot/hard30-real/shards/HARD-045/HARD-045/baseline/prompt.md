You are Codex working on a coding benchmark task.

Task ID: HARD-045
Category: stateful_regression
Repository hint: python/stream_window_join

User request:
Fix the streaming window joiner so out-of-order left/right events join within a time tolerance, watermarks evict only safely expired buffered events, duplicate event ids are ignored, late events are counted but not emitted, and snapshot() returns an isolated copy. Preserve WindowJoiner(tolerance_ms) with add_left, add_right, advance_watermark, and snapshot.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
