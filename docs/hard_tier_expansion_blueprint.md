# Hard-Tier Expansion Blueprint

This blueprint specifies the hard-tier expansion from the current evaluated
`hard10` pilot toward a 30-50 task hard tier. `HARD-011` and `HARD-012` are now
runnable fixtures; `HARD-013` through `HARD-030` are design candidates, not
claims that those tasks already exist as runnable fixtures.

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
| Hard tasks | 12 | 30 |
| Hard runs | 20 | 60 |
| Evaluated hard-pilot tasks | 10 | 30 |
| Hidden semantic tasks | 10 | 15 |
| Observable process-failure tasks | 2 | 10-15 |
| Process labels with positive examples | 1 | 4+ |

## Implemented And Candidate Tasks

| ID | Category | Repo hint | Public check | Hidden pressure | Expected failure pressure |
| --- | --- | --- | --- | --- | --- |
| HARD-011 | error_recovery | python/json_patch | `python3 -m unittest discover -s tests` | Implemented fixture; hidden tests cover move/copy edge cases and invalid pointer escaping. | `unrecovered_tool_error`, `verification_gap` |
| HARD-012 | dependency_friction | python/http_client | `python3 -m unittest discover -s tests` | Implemented fixture; hidden grader checks retry-after parsing without network access. | `sandbox_permission_deadlock`, `unrecovered_tool_error` |
| HARD-013 | multi_turn_change | typescript/filter_builder | `npm test` | Hidden tests require preserving previous filters after adding negation. | `context_drift`, `hidden_semantic_edge_case` |
| HARD-014 | refactor | python/permission_matrix | `python3 -m unittest discover -s tests` | Hidden tests ensure role inheritance and deny precedence survive refactor. | `verification_gap`, `hidden_semantic_edge_case` |
| HARD-015 | ci_failure | typescript/package_exports | `npm run build` | Hidden grader imports both ESM and CJS entry points. | `unrecovered_tool_error`, `premature_completion` |
| HARD-016 | bug_fix | python/time_window | `python3 -m unittest discover -s tests` | Hidden tests cover DST boundaries and half-open windows. | `hidden_semantic_edge_case` |
| HARD-017 | feature | typescript/batch_queue | `npm test` | Hidden tests cover cancellation, flush ordering, and rejected item isolation. | `repetitive_exploration`, `hidden_semantic_edge_case` |
| HARD-018 | error_localization | python/yaml_frontmatter | `python3 -m unittest discover -s tests` | Hidden tests cover malformed delimiters and empty documents. | `unrecovered_tool_error` |
| HARD-019 | multi_turn_change | python/search_ranker | `python3 -m unittest discover -s tests` | Hidden tests require exact-match boost without breaking recency tie-breaks. | `context_drift`, `hidden_semantic_edge_case` |
| HARD-020 | sandbox_friction | typescript/asset_loader | `npm test` | Hidden grader forbids network and expects local fixture fallback. | `sandbox_permission_deadlock` |
| HARD-021 | bug_fix | python/currency_parser | `python3 -m unittest discover -s tests` | Hidden tests cover parentheses negatives, thousands separators, and locale-free decimals. | `hidden_semantic_edge_case` |
| HARD-022 | refactor | typescript/state_machine | `npm test` | Hidden tests ensure invalid transitions preserve object identity. | `verification_gap`, `hidden_semantic_edge_case` |
| HARD-023 | error_recovery | python/cache_stampede | `python3 -m unittest discover -s tests` | Hidden tests cover concurrent failures and stale fallback behavior. | `unrecovered_tool_error`, `repetitive_exploration` |
| HARD-024 | feature | typescript/csv_stream | `npm test` | Hidden tests cover chunk boundaries inside quoted fields. | `hidden_semantic_edge_case` |
| HARD-025 | ci_failure | python/typing_protocol | `python3 -m unittest discover -s tests` | Hidden grader runs a protocol conformance check after visible tests. | `premature_completion`, `verification_gap` |
| HARD-026 | multi_turn_change | python/rules_engine | `python3 -m unittest discover -s tests` | Hidden tests require new priority rules while preserving legacy fallback. | `context_drift` |
| HARD-027 | dependency_friction | typescript/date_formatter | `npm test` | Hidden grader checks implementation without installing extra date libraries. | `sandbox_permission_deadlock`, `repetitive_exploration` |
| HARD-028 | bug_fix | python/path_normalizer | `python3 -m unittest discover -s tests` | Hidden tests cover Windows-style paths, dot segments, and root preservation. | `hidden_semantic_edge_case` |
| HARD-029 | refactor | typescript/validation_pipeline | `npm test` | Hidden tests ensure all validation errors are accumulated after refactor. | `verification_gap`, `context_drift` |
| HARD-030 | error_localization | python/template_renderer | `python3 -m unittest discover -s tests` | Hidden tests cover escaped braces and missing-variable diagnostics. | `unrecovered_tool_error`, `premature_completion` |

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

1. Implement HARD-013 to HARD-015 next because they target observable process
   failures missing from the current hard10 pilot.
2. Run dry-run materialization to confirm prompts and hidden grader isolation.
3. Run initial fixture checks and confirm every hidden grader fails before
   agent edits.
4. Collect baseline/intervention runs for the first five tasks.
5. Label failures manually before adding the next batch.

This staged approach avoids building 20 new tasks before learning whether the
new task designs actually produce the failure diversity needed for RQ1/RQ2/RQ4.
