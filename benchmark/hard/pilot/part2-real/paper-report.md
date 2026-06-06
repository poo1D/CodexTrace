# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

No failure tags were observed in these runs.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.6 | 0.6 | 0 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 8.8 | 5.6 | -3.2 |
| avg_retry_count | 0 | 0 | 0 |
| avg_command_failures | 0 | 0 | 0 |
| avg_token_usage | 2.485e+05 | 1.704e+05 | -7.81e+04 |
| avg_failure_score | 0 | 0 | 0 |
| avg_recover_events | 0 | 0 | 0 |
| avg_verify_events | 6.6 | 2 | -4.6 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=4, success=6, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1 | 1 | 0 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 7.75 | 6.833 | -0.9167 |
| retry_count | 0 | 0 | 0 |
| command_failure_count | 0 | 0 | 0 |
| token_usage | 2.155e+05 | 2.055e+05 | -9992 |
| failure_score | 0 | 0 | 0 |
| turn_count | 1 | 1 | 0 |
| time_to_first_edit | 14 | 14.33 | 0.3333 |
| time_to_first_test | 18.5 | 19.5 | 1 |
| phase_inspect_events | 11 | 11.33 | 0.3333 |
| phase_edit_events | 4 | 6 | 2 |
| phase_verify_events | 5.75 | 3.333 | -2.417 |
| phase_recover_events | 0 | 0 | 0 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| HARD-006 | baseline | failure | 0 | - |
| HARD-006 | intervention | failure | 0 | - |
| HARD-007 | baseline | success | 0 | - |
| HARD-007 | intervention | success | 0 | - |
| HARD-008 | baseline | success | 0 | - |
| HARD-008 | intervention | success | 0 | - |
| HARD-009 | baseline | failure | 0 | - |
| HARD-009 | intervention | failure | 0 | - |
| HARD-010 | baseline | success | 0 | - |
| HARD-010 | intervention | success | 0 | - |
