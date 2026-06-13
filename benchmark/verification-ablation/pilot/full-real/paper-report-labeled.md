# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

| Failure tag | Count | Percentage | Example task |
| --- | ---: | ---: | --- |
| verification_gap | 4 | 44.44 | VAB-001/baseline |
| premature_completion | 3 | 33.33 | VAB-001/baseline |
| hidden_semantic_edge_case | 2 | 22.22 | VAB-002/baseline |

## RQ2 Detector Agreement

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 2 | 0 | 0 | 0 |
| premature_completion | 3 | 0 | 0 | 1 | 1 | 1 |
| verification_gap | 4 | 0 | 0 | 1 | 1 | 1 |

Micro F1: 0.875; Macro F1: 0.6667.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.75 | 0.75 | 0 |
| verification_rate | 0 | 1 | 1 |
| success_check_verification_rate | 0 | 1 | 1 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 4 | 5.25 | 1.25 |
| avg_retry_count | 0 | 0 | 0 |
| avg_command_failures | 0 | 0 | 0 |
| avg_turn_count | 1 | 1 | 0 |
| avg_time_to_first_edit | 12.25 | 13.5 | 1.25 |
| avg_time_to_first_test | 0 | 16.5 | 16.5 |
| avg_token_usage | 1.458e+05 | 1.721e+05 | 2.632e+04 |
| avg_failure_score | 61.25 | 0 | -61.25 |
| avg_recover_events | 0 | 0 | 0 |
| avg_verify_events | 0 | 2 | 2 |

### Paired Task Summary

| Metric | Improved | Regressed | Unchanged | Average delta |
| --- | ---: | ---: | ---: | ---: |
| success | 0 | 0 | 4 | 0 |
| verification | 4 | 0 | 0 | 1 |
| success check verification | 4 | 0 | 0 | 1 |
| repeated tool calls | 0 | 3 | 1 | 1.25 |
| token usage | 1 | 3 | 0 | 2.632e+04 |
| failure score | 4 | 0 | 0 | -61.25 |

### Paired Task Deltas

| Task | Success delta | Verification delta | Success-check verification delta | Repeated calls delta | Token delta | Failure score delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| VAB-001 | 0 | 1 | 1 | 1 | 34563 | -70 |
| VAB-002 | 0 | 1 | 1 | 0 | -141 | -70 |
| VAB-003 | 0 | 1 | 1 | 3 | 36087 | -35 |
| VAB-004 | 0 | 1 | 1 | 1 | 34757 | -70 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=2, success=6, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 0.5 | 0.5 | 0 |
| success_check_verification_rate | 0.5 | 0.5 | 0 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 5 | 4.5 | -0.5 |
| retry_count | 0 | 0 | 0 |
| command_failure_count | 0 | 0 | 0 |
| token_usage | 1.725e+05 | 1.544e+05 | -1.813e+04 |
| failure_score | 35 | 29.17 | -5.833 |
| turn_count | 1 | 1 | 0 |
| time_to_first_edit | 13 | 12.83 | -0.1667 |
| time_to_first_test | 8 | 8.333 | 0.3333 |
| phase_inspect_events | 10 | 9.833 | -0.1667 |
| phase_edit_events | 4 | 2.667 | -1.333 |
| phase_verify_events | 1 | 1 | 0 |
| phase_recover_events | 0 | 0 | 0 |

## RQ4 Trace Signals By Manual Label

| Label | Runs | Signal | Mean | Overall mean | Delta label-overall |
| --- | ---: | --- | ---: | ---: | ---: |
| hidden_semantic_edge_case | 2 | verification_rate | 0.5 | 0.5 | 0 |
| hidden_semantic_edge_case | 2 | success_check_verification_rate | 0.5 | 0.5 | 0 |
| hidden_semantic_edge_case | 2 | unresolved_error | 0 | 0 | 0 |
| hidden_semantic_edge_case | 2 | repeated_tool_call_count | 5 | 5 | 0 |
| hidden_semantic_edge_case | 2 | retry_count | 0 | 0 | 0 |
| hidden_semantic_edge_case | 2 | command_failure_count | 0 | 0 | 0 |
| hidden_semantic_edge_case | 2 | token_usage | 1.725e+05 | 1.725e+05 | 0 |
| hidden_semantic_edge_case | 2 | failure_score | 35 | 35 | 0 |
| hidden_semantic_edge_case | 2 | turn_count | 1 | 1 | 0 |
| hidden_semantic_edge_case | 2 | time_to_first_edit | 13 | 13 | 0 |
| hidden_semantic_edge_case | 2 | time_to_first_test | 8 | 8 | 0 |
| hidden_semantic_edge_case | 2 | phase_inspect_events | 10 | 10 | 0 |
| hidden_semantic_edge_case | 2 | phase_edit_events | 4 | 4 | 0 |
| hidden_semantic_edge_case | 2 | phase_verify_events | 1 | 1 | 0 |
| hidden_semantic_edge_case | 2 | phase_recover_events | 0 | 0 | 0 |
| premature_completion | 3 | verification_rate | 0 | 0.5 | -0.5 |
| premature_completion | 3 | success_check_verification_rate | 0 | 0.5 | -0.5 |
| premature_completion | 3 | unresolved_error | 0 | 0 | 0 |
| premature_completion | 3 | repeated_tool_call_count | 4.333 | 5 | -0.6667 |
| premature_completion | 3 | retry_count | 0 | 0 | 0 |
| premature_completion | 3 | command_failure_count | 0 | 0 | 0 |
| premature_completion | 3 | token_usage | 1.489e+05 | 1.725e+05 | -2.366e+04 |
| premature_completion | 3 | failure_score | 70 | 35 | 35 |
| premature_completion | 3 | turn_count | 1 | 1 | 0 |
| premature_completion | 3 | time_to_first_edit | 13 | 13 | 0 |
| premature_completion | 3 | time_to_first_test | 0 | 8 | -8 |
| premature_completion | 3 | phase_inspect_events | 10 | 10 | 0 |
| premature_completion | 3 | phase_edit_events | 3 | 4 | -1 |
| premature_completion | 3 | phase_verify_events | 0 | 1 | -1 |
| premature_completion | 3 | phase_recover_events | 0 | 0 | 0 |
| verification_gap | 4 | verification_rate | 0 | 0.5 | -0.5 |
| verification_gap | 4 | success_check_verification_rate | 0 | 0.5 | -0.5 |
| verification_gap | 4 | unresolved_error | 0 | 0 | 0 |
| verification_gap | 4 | repeated_tool_call_count | 4 | 5 | -1 |
| verification_gap | 4 | retry_count | 0 | 0 | 0 |
| verification_gap | 4 | command_failure_count | 0 | 0 | 0 |
| verification_gap | 4 | token_usage | 1.458e+05 | 1.725e+05 | -2.676e+04 |
| verification_gap | 4 | failure_score | 61.25 | 35 | 26.25 |
| verification_gap | 4 | turn_count | 1 | 1 | 0 |
| verification_gap | 4 | time_to_first_edit | 12.25 | 13 | -0.75 |
| verification_gap | 4 | time_to_first_test | 0 | 8 | -8 |
| verification_gap | 4 | phase_inspect_events | 9.25 | 10 | -0.75 |
| verification_gap | 4 | phase_edit_events | 3 | 4 | -1 |
| verification_gap | 4 | phase_verify_events | 0 | 1 | -1 |
| verification_gap | 4 | phase_recover_events | 0 | 0 | 0 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| VAB-001 | baseline | success | 70 | premature_completion, verification_gap |
| VAB-001 | intervention | success | 0 | - |
| VAB-002 | baseline | failure | 70 | hidden_semantic_edge_case, premature_completion, verification_gap |
| VAB-002 | intervention | failure | 0 | hidden_semantic_edge_case |
| VAB-003 | baseline | success | 35 | verification_gap |
| VAB-003 | intervention | success | 0 | - |
| VAB-004 | baseline | success | 70 | premature_completion, verification_gap |
| VAB-004 | intervention | success | 0 | - |
