# Hard-Tier Expansion Blueprint

This blueprint specifies the hard-tier expansion from the current evaluated
`hard10` pilot toward a 30-50 task hard tier. `HARD-011` through `HARD-044` are
now runnable fixtures; later IDs are expansion candidates, not claims that
those tasks already exist as runnable fixtures.

The goal is to create more outcome failures and, importantly, more observable
process-failure positives for detector evaluation.

## Design Rules

- Each task must have a visible `public_success_check`.
- Hidden graders must be copied only after the Codex run exits.
- Initial fixtures must fail the hidden `success_check` before agent edits.
- Prompts must not reveal hidden edge-case details.
- Every task should name its expected failure pressure so later manual labels
  can be compared against the intended design.

## Target Mix

| Target | Current | Expansion target |
| --- | ---: | ---: |
| Hard tasks | 44 | 30-50 |
| Hard runs | 20 | 60 |
| Evaluated hard-pilot tasks | 10 | 30 |
| Hidden semantic tasks | 15 | 15 |
| Observable process-failure tasks | 13 | 10-15 |
| Process labels with positive examples | 1 | 4+ |

## Implemented And Candidate Tasks

| ID | Category | Repo hint | Public check | Hidden pressure | Expected failure pressure |
| --- | --- | --- | --- | --- | --- |
| HARD-011 | error_recovery | python/json_patch | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover move/copy edge cases and invalid pointer escaping. | `unrecovered_tool_error`, `verification_gap` |
| HARD-012 | dependency_friction | python/http_client | `python3 -m unittest discover -s tests` | Implemented fixture; hidden grader checks retry-after parsing without network access. | `sandbox_permission_deadlock`, `unrecovered_tool_error` |
| HARD-013 | multi_turn_change | typescript/filter_builder | `npm test` | Implemented fixture; hidden tests require preserving previous filters after adding negation. | `context_drift`, `hidden_semantic_edge_case` |
| HARD-014 | refactor | python/permission_matrix | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests ensure role inheritance and deny precedence survive refactor. | `verification_gap`, `hidden_semantic_edge_case` |
| HARD-015 | ci_failure | typescript/package_exports | `npm run build` | Implemented fixture; hidden grader imports both ESM and CJS entry points. | `unrecovered_tool_error`, `premature_completion` |
| HARD-016 | bug_fix | python/time_window | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover DST boundaries, half-open windows, and invalid windows. | `hidden_semantic_edge_case` |
| HARD-017 | feature | typescript/batch_queue | `npm test` | Implemented fixture; hidden tests cover cancellation, flush ordering, and rejected item isolation. | `repetitive_exploration`, `hidden_semantic_edge_case` |
| HARD-018 | error_localization | python/yaml_frontmatter | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover malformed delimiters, empty documents, and colons inside values. | `unrecovered_tool_error` |
| HARD-019 | multi_turn_change | python/search_ranker | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests require exact-match boost without breaking recency tie-breaks. | `context_drift`, `hidden_semantic_edge_case` |
| HARD-020 | sandbox_friction | typescript/asset_loader | `npm test` | Implemented fixture; hidden grader forbids network and expects local fixture fallback. | `sandbox_permission_deadlock` |
| HARD-021 | bug_fix | python/currency_parser | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover parentheses negatives, thousands separators, currency codes, and locale-free decimals. | `hidden_semantic_edge_case` |
| HARD-022 | refactor | typescript/state_machine | `npm test` | Implemented fixture; hidden tests ensure invalid transitions preserve object identity and a reusable transition helper exists. | `verification_gap`, `hidden_semantic_edge_case` |
| HARD-023 | error_recovery | python/cache_stampede | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover concurrent failures, stale fallback, failed cold-load retry, and different-key nonblocking behavior. | `unrecovered_tool_error`, `repetitive_exploration`, `verification_gap` |
| HARD-024 | feature | typescript/csv_stream | `npm test` | Implemented fixture; hidden tests cover chunk boundaries inside quoted fields, escaped quotes, quoted newlines, CRLF, and malformed quote errors. | `hidden_semantic_edge_case`, `verification_gap` |
| HARD-025 | ci_failure | python/typing_protocol | `python3 -m unittest discover -s tests` | Implemented fixture; hidden grader checks runtime-checkable Protocol conformance and foreign structural writers after visible CI failures. | `premature_completion`, `verification_gap`, `hidden_semantic_edge_case` |
| HARD-026 | multi_turn_change | python/rules_engine | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests require priority tie stability, explicit zero/negative priorities, legacy fallback, defaults, and input preservation. | `context_drift`, `hidden_semantic_edge_case` |
| HARD-027 | dependency_friction | typescript/date_formatter | `npm test` | Implemented fixture; hidden grader checks deterministic UTC formatting, fixed offsets, literals, invalid dates, and no external date-library dependencies. | `sandbox_permission_deadlock`, `repetitive_exploration`, `hidden_semantic_edge_case` |
| HARD-028 | bug_fix | python/path_normalizer | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover Windows separators, drive roots, UNC roots, leading parents, POSIX absolute roots, and deterministic forward slashes. | `hidden_semantic_edge_case`, `verification_gap` |
| HARD-029 | refactor | typescript/validation_pipeline | `npm test` | Implemented fixture; hidden tests ensure all validation errors are accumulated in stable order while valid-user normalization and input immutability survive the refactor. | `verification_gap`, `context_drift` |
| HARD-030 | error_localization | python/template_renderer | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover escaped braces, stringification of present falsey values, and missing-variable line/column diagnostics. | `unrecovered_tool_error`, `premature_completion` |
| HARD-031 | multi_turn_tool_debug | python/env_manifest_resolver | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover cwd-sensitive manifest resolution, env precedence, blank local overrides, explicit empty CLI overrides, and stable JSON output. | `verification_gap`, `premature_completion`, `repetitive_exploration`, `unrecovered_tool_error` |
| HARD-032 | stateful_regression | typescript/undoable_queue | `npm test` | Implemented fixture; hidden tests cover undo/redo metadata preservation, snapshot isolation, clear/redo semantics, and FIFO order after consecutive history operations. | `verification_gap`, `premature_completion`, `context_drift`, `repetitive_exploration` |
| HARD-033 | error_recovery | python/log_redactor | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover credential redaction across text, URL query strings, authorization headers, nested structured events, and input immutability. | `unrecovered_tool_error`, `verification_gap`, `premature_completion` |
| HARD-034 | multi_turn_change | python/feature_flags | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover deterministic rollout buckets, allow/deny user overrides, missing-flag defaults, and input immutability. | `context_drift`, `verification_gap`, `hidden_semantic_edge_case` |
| HARD-035 | dependency_friction | python/retry_policy | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover retryable status filtering, Retry-After seconds and HTTP-date parsing, max-delay caps, and input immutability without external dependencies. | `sandbox_permission_deadlock`, `verification_gap`, `hidden_semantic_edge_case` |
| HARD-036 | feature | typescript/metrics_window | `npm test` | Implemented fixture; hidden tests cover inclusive lower-bound windows, deterministic nearest-rank p95, future-event exclusion, zero-width windows, and input immutability. | `hidden_semantic_edge_case`, `verification_gap`, `context_drift` |
| HARD-037 | stateful_regression | python/sliding_limiter | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover rolling-window boundaries, per-user isolation, injected-clock usage, rejected-request recording, and stale event pruning. | `hidden_semantic_edge_case`, `verification_gap`, `premature_completion` |
| HARD-038 | error_localization | typescript/source_map_ranges | `npm test` | Implemented fixture; hidden tests cover nearest-preceding source-map segments, multi-line generated ranges, zero-based columns, stable segment ordering, and diagnostic errors for malformed mappings. | `unrecovered_tool_error`, `hidden_semantic_edge_case`, `repetitive_exploration` |
| HARD-039 | multi_turn_tool_debug | python/cli_report_writer | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover cwd-independent input resolution, parent directory creation, deterministic JSON/text rendering, atomic writes, and cleanup after render failures. | `sandbox_permission_deadlock`, `unrecovered_tool_error`, `premature_completion`, `verification_gap` |
| HARD-040 | stateful_regression | python/ledger_reconciler | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover atomic batch application, duplicate event ids, single-use reversals, currency mismatch errors, and input immutability. | `verification_gap`, `hidden_semantic_edge_case`, `context_drift` |
| HARD-041 | feature | typescript/range_set | `npm test` | Implemented fixture; hidden tests cover immutable interval operations, adjacent coalescing, split removals, negative ranges, union normalization, and invalid-bound errors. | `hidden_semantic_edge_case`, `verification_gap`, `context_drift` |
| HARD-042 | multi_turn_tool_debug | python/snapshot_manifest | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover cwd-independent manifest generation, ignore patterns, SHA-256 content hashes, forward-slash paths, deterministic ordering, and optional empty directories. | `verification_gap`, `premature_completion`, `unrecovered_tool_error` |
| HARD-043 | data_migration | python/migration_runner | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover dependency ordering, checksum drift, rollback after failed migrations, already-applied skips, and diagnostics for missing dependencies or cycles. | `verification_gap`, `context_drift`, `hidden_semantic_edge_case` |
| HARD-044 | feature | typescript/icu_plural_format | `npm test` | Implemented fixture; hidden tests cover ICU plural exact arms, one/other selection, offsets, `#` substitution, escaped apostrophes, missing-value diagnostics, and input immutability. | `hidden_semantic_edge_case`, `verification_gap`, `unrecovered_tool_error` |

## Manual Labeling Target

After collecting these tasks, manual labels should aim for at least:

| Label | Minimum positive examples |
| --- | ---: |
| `verification_gap` | 3 |
| `unrecovered_tool_error` | 3 |
| `repetitive_exploration` | 2 |
| `context_drift` | 3 |
| `premature_completion` | 2 |
| `sandbox_permission_deadlock` | 2 |
| `hidden_semantic_edge_case` | 8 |

## Implementation Order

1. Design and implement HARD-045 with a new observable process-failure pressure.
2. Run dry-run materialization to confirm prompts and hidden grader isolation.
3. Run initial fixture checks and confirm every hidden grader fails before
   agent edits.
4. Collect baseline/intervention runs for the first five tasks.
5. Label failures manually before adding the next batch.

This staged approach avoids building 20 new tasks before learning whether the
new task designs actually produce the failure diversity needed for RQ1/RQ2/RQ4.
