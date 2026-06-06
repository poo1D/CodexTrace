# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

No failure tags were observed in these runs.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.7 | 0.8 | 0.1 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 9.2 | 6.2 | -3 |
| avg_retry_count | 0 | 0 | 0 |
| avg_command_failures | 0 | 0 | 0 |
| avg_token_usage | 2.489e+05 | 1.875e+05 | -6.145e+04 |
| avg_failure_score | 0 | 0 | 0 |
| avg_recover_events | 0 | 0 | 0 |
| avg_verify_events | 7.3 | 3.7 | -3.6 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=5, success=15, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1 | 1 | 0 |
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
