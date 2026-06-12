# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

| Failure tag | Count | Percentage | Example task |
| --- | ---: | ---: | --- |
| verification_gap | 4 | 57.14 | VAB-001/baseline |
| premature_completion | 3 | 42.86 | VAB-001/baseline |

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.75 | 0.75 | 0 |
| verification_rate | 0 | 1 | 1 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 4 | 5.25 | 1.25 |
| avg_retry_count | 0 | 0 | 0 |
| avg_command_failures | 0 | 0 | 0 |
| avg_token_usage | 1.458e+05 | 1.721e+05 | 2.632e+04 |
| avg_failure_score | 61.25 | 0 | -61.25 |
| avg_recover_events | 0 | 0 | 0 |
| avg_verify_events | 0 | 2 | 2 |

### Paired Task Summary

| Metric | Improved | Regressed | Unchanged | Average delta |
| --- | ---: | ---: | ---: | ---: |
| success | 0 | 0 | 4 | 0 |
| verification | 4 | 0 | 0 | 1 |
| repeated tool calls | 0 | 3 | 1 | 1.25 |
| token usage | 1 | 3 | 0 | 2.632e+04 |
| failure score | 4 | 0 | 0 | -61.25 |

### Paired Task Deltas

| Task | Success delta | Verification delta | Repeated calls delta | Token delta | Failure score delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| VAB-001 | 0 | 1 | 1 | 34563 | -70 |
| VAB-002 | 0 | 1 | 0 | -141 | -70 |
| VAB-003 | 0 | 1 | 3 | 36087 | -35 |
| VAB-004 | 0 | 1 | 1 | 34757 | -70 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=2, success=6, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 0.5 | 0.5 | 0 |
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

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| VAB-001 | baseline | success | 70 | verification_gap, premature_completion |
| VAB-001 | intervention | success | 0 | - |
| VAB-002 | baseline | failure | 70 | verification_gap, premature_completion |
| VAB-002 | intervention | failure | 0 | - |
| VAB-003 | baseline | success | 35 | verification_gap |
| VAB-003 | intervention | success | 0 | - |
| VAB-004 | baseline | success | 70 | verification_gap, premature_completion |
| VAB-004 | intervention | success | 0 | - |
