# Hard30 Task Diagnosis

This generated audit answers which hard30 tasks are easiest for the agent to get lost in, and where the intervention reduces or worsens process waste.

## Summary

- Tasks: 30
- Both failed: 14
- Intervention repaired: 1
- Intervention regressed: 1
- Both succeeded: 14
- Token usage improved: 26/30
- Repeated tool calls improved: 26/30

## Failure Patterns

| Pattern | Count |
| --- | ---: |
| both_failed | 14 |
| both_succeeded | 14 |
| intervention_regressed | 1 |
| intervention_repaired | 1 |

## Double-Failure Tasks

| Task | Category | Repo | Tags | Repeated-call delta | Token delta |
| --- | --- | --- | --- | ---: | ---: |
| HARD-001 | bug_fix | python/interval_merge | hidden_semantic_edge_case | -3 | -69768 |
| HARD-006 | feature | typescript/retry | hidden_semantic_edge_case | -3 | -73787 |
| HARD-009 | multi_turn_change | python/booking_policy | hidden_semantic_edge_case | 0 | -35606 |
| HARD-012 | dependency_friction | python/http_client | hidden_semantic_edge_case | -2 | -39944 |
| HARD-013 | multi_turn_change | typescript/filter_builder | hidden_semantic_edge_case | -9 | -235860 |
| HARD-015 | ci_failure | typescript/package_exports | hidden_semantic_edge_case | -5 | -111558 |
| HARD-027 | dependency_friction | typescript/date_formatter | hidden_semantic_edge_case | -11 | -204667 |
| HARD-032 | stateful_regression | typescript/undoable_queue | hidden_semantic_edge_case | -3 | -40264 |
| HARD-033 | error_recovery | python/log_redactor | hidden_semantic_edge_case, repetitive_exploration | -15 | -699231 |
| HARD-035 | dependency_friction | python/retry_policy | hidden_semantic_edge_case | -1 | 33439 |
| HARD-038 | error_localization | typescript/source_map_ranges | hidden_semantic_edge_case | -3 | -86667 |
| HARD-040 | stateful_regression | python/ledger_reconciler | hidden_semantic_edge_case | -2 | -47757 |
| HARD-043 | data_migration | python/migration_runner | hidden_semantic_edge_case | -4 | -118044 |
| HARD-045 | stateful_regression | python/stream_window_join | hidden_semantic_edge_case | -4 | -76776 |

## Intervention Repairs And Regressions

| Task | Pattern | Category | Repo | Repeated-call delta | Token delta |
| --- | --- | --- | --- | ---: | ---: |
| HARD-050 | intervention_repaired | multi_turn_change | python/config_overlay_resolver | -4 | -170828 |
| HARD-007 | intervention_regressed | refactor | python/config_merge | -2 | -72244 |

## Largest Waste Reductions

| Task | Pattern | Category | Repo | Repeated-call delta | Token delta | Failure-score delta |
| --- | --- | --- | --- | ---: | ---: | ---: |
| HARD-033 | both_failed | error_recovery | python/log_redactor | -15 | -699231 | -35 |
| HARD-013 | both_failed | multi_turn_change | typescript/filter_builder | -9 | -235860 | -5 |
| HARD-024 | both_succeeded | feature | typescript/csv_stream | -5 | -218376 | 5 |
| HARD-011 | both_succeeded | error_recovery | python/json_patch | -6 | -216568 | -30 |
| HARD-027 | both_failed | dependency_friction | typescript/date_formatter | -11 | -204667 | -5 |

## Largest Waste Regressions

| Task | Pattern | Category | Repo | Repeated-call delta | Token delta | Failure-score delta |
| --- | --- | --- | --- | ---: | ---: | ---: |
| HARD-031 | both_succeeded | multi_turn_tool_debug | python/env_manifest_resolver | 5 | 111523 | 0 |
| HARD-039 | both_succeeded | multi_turn_tool_debug | python/cli_report_writer | 1 | 80525 | 0 |
| HARD-005 | both_succeeded | bug_fix | typescript/router | 0 | 71341 | 0 |
| HARD-035 | both_failed | dependency_friction | python/retry_policy | -1 | 33439 | 0 |
| HARD-004 | both_succeeded | error_localization | python/toposort | -2 | -9556 | 0 |

Interpretation: the current hard30 artifact is dominated by hidden semantic double failures, while the intervention's clearest task-level effect is lower token and repeated-call waste on most paired tasks. `HARD-050` is the one hard30 repair, and `HARD-007` is the one hard30 outcome regression.
