You are Codex working on a coding benchmark task.

Task ID: HARD-038
Category: error_localization
Repository hint: typescript/source_map_ranges

User request:
Fix source-position mapping so generated line and column ranges map to original positions using the nearest preceding mapping segment, support multi-line generated ranges, preserve zero-based columns, and raise SourceMapError with useful diagnostics for malformed mappings. Preserve mapRange(map, start, end).

Success check:
npm test

Complete the task with your normal coding workflow.
