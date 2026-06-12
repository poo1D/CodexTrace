# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

| Failure tag | Count | Percentage | Example task |
| --- | ---: | ---: | --- |
| hidden_semantic_edge_case | 2 | 100 | PST-002/baseline |

## RQ2 Detector Agreement

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 2 | 0 | 0 | 0 |

Micro F1: 0; Macro F1: 0.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.9167 | 0.9167 | 0 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 8.083 | 7.167 | -0.9166 |
| avg_retry_count | 0.1667 | 0.25 | 0.0833 |
| avg_command_failures | 0.25 | 0.25 | 0 |
| avg_token_usage | 2.09e+05 | 1.851e+05 | -2.387e+04 |
| avg_failure_score | 1.25 | 1.25 | 0 |
| avg_recover_events | 1.25 | 0.8333 | -0.4167 |
| avg_verify_events | 5 | 4.417 | -0.5833 |

### Paired Task Summary

| Metric | Improved | Regressed | Unchanged | Average delta |
| --- | ---: | ---: | ---: | ---: |
| success | 0 | 0 | 12 | 0 |
| verification | 0 | 0 | 12 | 0 |
| repeated tool calls | 4 | 3 | 5 | -0.9167 |
| token usage | 5 | 7 | 0 | -2.387e+04 |
| failure score | 0 | 0 | 12 | 0 |

### Paired Task Deltas

| Task | Success delta | Verification delta | Repeated calls delta | Token delta | Failure score delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| PST-001 | 0 | 0 | 0 | 288 | 0 |
| PST-002 | 0 | 0 | -3 | -72615 | 0 |
| PST-003 | 0 | 0 | 0 | 36102 | 0 |
| PST-004 | 0 | 0 | 0 | -34437 | 0 |
| PST-005 | 0 | 0 | -2 | -36751 | 0 |
| PST-006 | 0 | 0 | 3 | 34976 | 0 |
| PST-007 | 0 | 0 | 1 | 1753 | 0 |
| PST-008 | 0 | 0 | -3 | -74629 | 0 |
| PST-009 | 0 | 0 | 0 | 290 | 0 |
| PST-010 | 0 | 0 | 2 | 36189 | 0 |
| PST-011 | 0 | 0 | 0 | 1145 | 0 |
| PST-012 | 0 | 0 | -9 | -178732 | 0 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=2, success=22, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1 | 1 | 0 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 6.5 | 7.727 | 1.227 |
| retry_count | 0 | 0.2273 | 0.2273 |
| command_failure_count | 0 | 0.2727 | 0.2727 |
| token_usage | 2.11e+05 | 1.958e+05 | -1.519e+04 |
| failure_score | 0 | 1.364 | 1.364 |
| turn_count | 1 | 1 | 0 |
| time_to_first_edit | 13 | 15.77 | 2.773 |
| time_to_first_test | 12 | 16.59 | 4.591 |
| phase_inspect_events | 6 | 11.09 | 5.091 |
| phase_edit_events | 4.5 | 3.409 | -1.091 |
| phase_verify_events | 8.5 | 4.364 | -4.136 |
| phase_recover_events | 0 | 1.136 | 1.136 |

## RQ4 Trace Signals By Manual Label

| Label | Runs | Signal | Mean | Overall mean | Delta label-overall |
| --- | ---: | --- | ---: | ---: | ---: |
| hidden_semantic_edge_case | 2 | verification_rate | 1 | 1 | 0 |
| hidden_semantic_edge_case | 2 | unresolved_error | 0 | 0 | 0 |
| hidden_semantic_edge_case | 2 | repeated_tool_call_count | 6.5 | 6.5 | 0 |
| hidden_semantic_edge_case | 2 | retry_count | 0 | 0 | 0 |
| hidden_semantic_edge_case | 2 | command_failure_count | 0 | 0 | 0 |
| hidden_semantic_edge_case | 2 | token_usage | 2.11e+05 | 2.11e+05 | 0 |
| hidden_semantic_edge_case | 2 | failure_score | 0 | 0 | 0 |
| hidden_semantic_edge_case | 2 | turn_count | 1 | 1 | 0 |
| hidden_semantic_edge_case | 2 | time_to_first_edit | 13 | 13 | 0 |
| hidden_semantic_edge_case | 2 | time_to_first_test | 12 | 12 | 0 |
| hidden_semantic_edge_case | 2 | phase_inspect_events | 6 | 6 | 0 |
| hidden_semantic_edge_case | 2 | phase_edit_events | 4.5 | 4.5 | 0 |
| hidden_semantic_edge_case | 2 | phase_verify_events | 8.5 | 8.5 | 0 |
| hidden_semantic_edge_case | 2 | phase_recover_events | 0 | 0 | 0 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| PST-001 | baseline | success | 0 | - |
| PST-001 | intervention | success | 0 | - |
| PST-002 | baseline | failure | 0 | hidden_semantic_edge_case |
| PST-002 | intervention | failure | 0 | hidden_semantic_edge_case |
| PST-003 | baseline | success | 5 | - |
| PST-003 | intervention | success | 5 | - |
| PST-004 | baseline | success | 5 | - |
| PST-004 | intervention | success | 5 | - |
| PST-005 | baseline | success | 0 | - |
| PST-005 | intervention | success | 0 | - |
| PST-006 | baseline | success | 5 | - |
| PST-006 | intervention | success | 5 | - |
| PST-007 | baseline | success | 0 | - |
| PST-007 | intervention | success | 0 | - |
| PST-008 | baseline | success | 0 | - |
| PST-008 | intervention | success | 0 | - |
| PST-009 | baseline | success | 0 | - |
| PST-009 | intervention | success | 0 | - |
| PST-010 | baseline | success | 0 | - |
| PST-010 | intervention | success | 0 | - |
| PST-011 | baseline | success | 0 | - |
| PST-011 | intervention | success | 0 | - |
| PST-012 | baseline | success | 0 | - |
| PST-012 | intervention | success | 0 | - |
