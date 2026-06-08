You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-038
Category: error_localization
Repository hint: typescript/source_map_ranges

User request:
Fix source-position mapping so generated line and column ranges map to original positions using the nearest preceding mapping segment, support multi-line generated ranges, preserve zero-based columns, and raise SourceMapError with useful diagnostics for malformed mappings. Preserve mapRange(map, start, end).

Success check:
npm test

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
