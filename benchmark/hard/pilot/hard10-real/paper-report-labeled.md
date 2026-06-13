# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

| Failure tag | Count | Percentage | Example task |
| --- | ---: | ---: | --- |
| hidden_semantic_edge_case | 5 | 100 | HARD-001/baseline |

## RQ2 Detector Agreement

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 5 | 0 | 0 | 0 |

Micro F1: 0; Macro F1: 0.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.7 | 0.8 | 0.1 |
| verification_rate | 1 | 1 | 0 |
| success_check_verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 9.2 | 6.2 | -3 |
| avg_retry_count | 0 | 0 | 0 |
| avg_command_failures | 0 | 0 | 0 |
| avg_turn_count | 1 | 1 | 0 |
| avg_time_to_first_edit | 14.2 | 13.8 | -0.4 |
| avg_time_to_first_test | 19 | 17.4 | -1.6 |
| avg_token_usage | 2.489e+05 | 1.875e+05 | -6.145e+04 |
| avg_failure_score | 0 | 0 | 0 |
| avg_recover_events | 0 | 0 | 0 |
| avg_verify_events | 7.3 | 3.7 | -3.6 |

### Paired Task Summary

| Metric | Improved | Regressed | Unchanged | Average delta |
| --- | ---: | ---: | ---: | ---: |
| success | 1 | 0 | 9 | 0.1 |
| verification | 0 | 0 | 10 | 0 |
| success check verification | 0 | 0 | 10 | 0 |
| repeated tool calls | 9 | 1 | 0 | -3 |
| token usage | 9 | 1 | 0 | -6.145e+04 |
| failure score | 0 | 0 | 10 | 0 |

### Paired Task Deltas

| Task | Success delta | Verification delta | Success-check verification delta | Repeated calls delta | Token delta | Failure score delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| HARD-001 | 1 | 0 | 0 | -4 | -102386 | 0 |
| HARD-002 | 0 | 0 | 0 | 2 | 34062 | 0 |
| HARD-003 | 0 | 0 | 0 | -2 | -35359 | 0 |
| HARD-004 | 0 | 0 | 0 | -9 | -116010 | 0 |
| HARD-005 | 0 | 0 | 0 | -1 | -4290 | 0 |
| HARD-006 | 0 | 0 | 0 | -3 | -37533 | 0 |
| HARD-007 | 0 | 0 | 0 | -1 | -35238 | 0 |
| HARD-008 | 0 | 0 | 0 | -1 | -35537 | 0 |
| HARD-009 | 0 | 0 | 0 | -6 | -101031 | 0 |
| HARD-010 | 0 | 0 | 0 | -5 | -181152 | 0 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=5, success=15, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1 | 1 | 0 |
| success_check_verification_rate | 1 | 1 | 0 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 8 | 7.6 | -0.4 |
| retry_count | 0 | 0 | 0 |
| command_failure_count | 0 | 0 | 0 |
| token_usage | 2.256e+05 | 2.157e+05 | -9853 |
| failure_score | 0 | 0 | 0 |
| turn_count | 1 | 1 | 0 |
| time_to_first_edit | 13.8 | 14.07 | 0.2667 |
| time_to_first_test | 19 | 17.93 | -1.067 |
| phase_inspect_events | 10.8 | 10.4 | -0.4 |
| phase_edit_events | 5.8 | 5.933 | 0.1333 |
| phase_verify_events | 5.6 | 5.467 | -0.1333 |
| phase_recover_events | 0 | 0 | 0 |

## RQ4 Trace Signals By Manual Label

| Label | Runs | Signal | Mean | Overall mean | Delta label-overall |
| --- | ---: | --- | ---: | ---: | ---: |
| hidden_semantic_edge_case | 5 | verification_rate | 1 | 1 | 0 |
| hidden_semantic_edge_case | 5 | success_check_verification_rate | 1 | 1 | 0 |
| hidden_semantic_edge_case | 5 | unresolved_error | 0 | 0 | 0 |
| hidden_semantic_edge_case | 5 | repeated_tool_call_count | 8 | 8 | 0 |
| hidden_semantic_edge_case | 5 | retry_count | 0 | 0 | 0 |
| hidden_semantic_edge_case | 5 | command_failure_count | 0 | 0 | 0 |
| hidden_semantic_edge_case | 5 | token_usage | 2.256e+05 | 2.256e+05 | 0 |
| hidden_semantic_edge_case | 5 | failure_score | 0 | 0 | 0 |
| hidden_semantic_edge_case | 5 | turn_count | 1 | 1 | 0 |
| hidden_semantic_edge_case | 5 | time_to_first_edit | 13.8 | 13.8 | 0 |
| hidden_semantic_edge_case | 5 | time_to_first_test | 19 | 19 | 0 |
| hidden_semantic_edge_case | 5 | phase_inspect_events | 10.8 | 10.8 | 0 |
| hidden_semantic_edge_case | 5 | phase_edit_events | 5.8 | 5.8 | 0 |
| hidden_semantic_edge_case | 5 | phase_verify_events | 5.6 | 5.6 | 0 |
| hidden_semantic_edge_case | 5 | phase_recover_events | 0 | 0 | 0 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| HARD-001 | baseline | failure | 0 | hidden_semantic_edge_case |
| HARD-001 | intervention | success | 0 | - |
| HARD-002 | baseline | success | 0 | - |
| HARD-002 | intervention | success | 0 | - |
| HARD-003 | baseline | success | 0 | - |
| HARD-003 | intervention | success | 0 | - |
| HARD-004 | baseline | success | 0 | - |
| HARD-004 | intervention | success | 0 | - |
| HARD-005 | baseline | success | 0 | - |
| HARD-005 | intervention | success | 0 | - |
| HARD-006 | baseline | failure | 0 | hidden_semantic_edge_case |
| HARD-006 | intervention | failure | 0 | hidden_semantic_edge_case |
| HARD-007 | baseline | success | 0 | - |
| HARD-007 | intervention | success | 0 | - |
| HARD-008 | baseline | success | 0 | - |
| HARD-008 | intervention | success | 0 | - |
| HARD-009 | baseline | failure | 0 | hidden_semantic_edge_case |
| HARD-009 | intervention | failure | 0 | hidden_semantic_edge_case |
| HARD-010 | baseline | success | 0 | - |
| HARD-010 | intervention | success | 0 | - |
