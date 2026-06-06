# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

No failure tags were observed in these runs.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.8 | 1 | 0.2 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 9.6 | 6.8 | -2.8 |
| avg_retry_count | 0 | 0 | 0 |
| avg_command_failures | 0 | 0 | 0 |
| avg_token_usage | 2.493e+05 | 2.045e+05 | -4.48e+04 |
| avg_failure_score | 0 | 0 | 0 |
| avg_recover_events | 0 | 0 | 0 |
| avg_verify_events | 8 | 5.4 | -2.6 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=1, success=9, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1 | 1 | 0 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 9 | 8.111 | -0.8889 |
| retry_count | 0 | 0 | 0 |
| command_failure_count | 0 | 0 | 0 |
| token_usage | 2.66e+05 | 2.226e+05 | -4.348e+04 |
| failure_score | 0 | 0 | 0 |
| turn_count | 1 | 1 | 0 |
| time_to_first_edit | 13 | 13.89 | 0.8889 |
| time_to_first_test | 21 | 16.89 | -4.111 |
| phase_inspect_events | 10 | 9.778 | -0.2222 |
| phase_edit_events | 13 | 5.889 | -7.111 |
| phase_verify_events | 5 | 6.889 | 1.889 |
| phase_recover_events | 0 | 0 | 0 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| HARD-001 | baseline | failure | 0 | - |
| HARD-001 | intervention | success | 0 | - |
| HARD-002 | baseline | success | 0 | - |
| HARD-002 | intervention | success | 0 | - |
| HARD-003 | baseline | success | 0 | - |
| HARD-003 | intervention | success | 0 | - |
| HARD-004 | baseline | success | 0 | - |
| HARD-004 | intervention | success | 0 | - |
| HARD-005 | baseline | success | 0 | - |
| HARD-005 | intervention | success | 0 | - |
