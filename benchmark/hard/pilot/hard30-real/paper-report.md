# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

No failure tags were observed in these runs.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.5 | 0.5 | 0 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 12.93 | 9.2 | -3.733 |
| avg_retry_count | 0.2 | 0 | -0.2 |
| avg_command_failures | 0.3 | 0.1 | -0.2 |
| avg_token_usage | 3.55e+05 | 2.563e+05 | -9.866e+04 |
| avg_failure_score | 1.5 | 0.5 | -1 |
| avg_recover_events | 1.2 | 0.8333 | -0.3667 |
| avg_verify_events | 10.7 | 6.767 | -3.933 |

### Paired Task Summary

| Metric | Improved | Regressed | Unchanged | Average delta |
| --- | ---: | ---: | ---: | ---: |
| success | 1 | 1 | 28 | 0 |
| verification | 0 | 0 | 30 | 0 |
| repeated tool calls | 26 | 2 | 2 | -3.733 |
| token usage | 26 | 4 | 0 | -9.866e+04 |
| failure score | 4 | 1 | 25 | -1 |

### Paired Task Deltas

| Task | Success delta | Verification delta | Repeated calls delta | Token delta | Failure score delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| HARD-001 | 0 | 0 | -3 | -69768 | 0 |
| HARD-002 | 0 | 0 | -5 | -74603 | 0 |
| HARD-003 | 0 | 0 | -3 | -73318 | 0 |
| HARD-004 | 0 | 0 | -2 | -9556 | 0 |
| HARD-005 | 0 | 0 | 0 | 71341 | 0 |
| HARD-006 | 0 | 0 | -3 | -73787 | 0 |
| HARD-007 | -1 | 0 | -2 | -72244 | 0 |
| HARD-008 | 0 | 0 | -4 | -75974 | 0 |
| HARD-009 | 0 | 0 | 0 | -35606 | 0 |
| HARD-010 | 0 | 0 | -5 | -150279 | 0 |
| HARD-011 | 0 | 0 | -6 | -216568 | -10 |
| HARD-012 | 0 | 0 | -2 | -39944 | 0 |
| HARD-013 | 0 | 0 | -9 | -235860 | -5 |
| HARD-015 | 0 | 0 | -5 | -111558 | 0 |
| HARD-020 | 0 | 0 | -4 | -76225 | 0 |
| HARD-023 | 0 | 0 | -7 | -164714 | 0 |
| HARD-024 | 0 | 0 | -5 | -218376 | 5 |
| HARD-025 | 0 | 0 | -4 | -36371 | 0 |
| HARD-027 | 0 | 0 | -11 | -204667 | -5 |
| HARD-031 | 0 | 0 | 5 | 111523 | 0 |
| HARD-032 | 0 | 0 | -3 | -40264 | 0 |
| HARD-033 | 0 | 0 | -15 | -699231 | -15 |
| HARD-035 | 0 | 0 | -1 | 33439 | 0 |
| HARD-038 | 0 | 0 | -3 | -86667 | 0 |
| HARD-039 | 0 | 0 | 1 | 80525 | 0 |
| HARD-040 | 0 | 0 | -2 | -47757 | 0 |
| HARD-043 | 0 | 0 | -4 | -118044 | 0 |
| HARD-045 | 0 | 0 | -4 | -76776 | 0 |
| HARD-047 | 0 | 0 | -2 | -77546 | 0 |
| HARD-050 | 1 | 0 | -4 | -170828 | 0 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=30, success=30, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1 | 1 | 0 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 10.8 | 11.33 | 0.5333 |
| retry_count | 0.1333 | 0.0667 | -0.0666 |
| command_failure_count | 0.2333 | 0.1667 | -0.0666 |
| token_usage | 3.065e+05 | 3.048e+05 | -1772 |
| failure_score | 1.167 | 0.8333 | -0.3334 |
| turn_count | 1 | 1 | 0 |
| time_to_first_edit | 15.6 | 15.97 | 0.3667 |
| time_to_first_test | 19.27 | 20.3 | 1.033 |
| phase_inspect_events | 12.37 | 12.83 | 0.4666 |
| phase_edit_events | 7.133 | 6.5 | -0.6333 |
| phase_verify_events | 8.167 | 9.3 | 1.133 |
| phase_recover_events | 1.233 | 0.8 | -0.4333 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| HARD-001 | baseline | failure | 0 | - |
| HARD-001 | intervention | failure | 0 | - |
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
| HARD-007 | intervention | failure | 0 | - |
| HARD-008 | baseline | success | 0 | - |
| HARD-008 | intervention | success | 0 | - |
| HARD-009 | baseline | failure | 0 | - |
| HARD-009 | intervention | failure | 0 | - |
| HARD-010 | baseline | success | 0 | - |
| HARD-010 | intervention | success | 0 | - |
| HARD-011 | baseline | success | 10 | - |
| HARD-011 | intervention | success | 0 | - |
| HARD-012 | baseline | failure | 0 | - |
| HARD-012 | intervention | failure | 0 | - |
| HARD-013 | baseline | failure | 5 | - |
| HARD-013 | intervention | failure | 0 | - |
| HARD-015 | baseline | failure | 5 | - |
| HARD-015 | intervention | failure | 5 | - |
| HARD-020 | baseline | success | 0 | - |
| HARD-020 | intervention | success | 0 | - |
| HARD-023 | baseline | success | 0 | - |
| HARD-023 | intervention | success | 0 | - |
| HARD-024 | baseline | success | 0 | - |
| HARD-024 | intervention | success | 5 | - |
| HARD-025 | baseline | success | 0 | - |
| HARD-025 | intervention | success | 0 | - |
| HARD-027 | baseline | failure | 5 | - |
| HARD-027 | intervention | failure | 0 | - |
| HARD-031 | baseline | success | 0 | - |
| HARD-031 | intervention | success | 0 | - |
| HARD-032 | baseline | failure | 0 | - |
| HARD-032 | intervention | failure | 0 | - |
| HARD-033 | baseline | failure | 15 | - |
| HARD-033 | intervention | failure | 0 | - |
| HARD-035 | baseline | failure | 0 | - |
| HARD-035 | intervention | failure | 0 | - |
| HARD-038 | baseline | failure | 0 | - |
| HARD-038 | intervention | failure | 0 | - |
| HARD-039 | baseline | success | 5 | - |
| HARD-039 | intervention | success | 5 | - |
| HARD-040 | baseline | failure | 0 | - |
| HARD-040 | intervention | failure | 0 | - |
| HARD-043 | baseline | failure | 0 | - |
| HARD-043 | intervention | failure | 0 | - |
| HARD-045 | baseline | failure | 0 | - |
| HARD-045 | intervention | failure | 0 | - |
| HARD-047 | baseline | success | 0 | - |
| HARD-047 | intervention | success | 0 | - |
| HARD-050 | baseline | failure | 0 | - |
| HARD-050 | intervention | success | 0 | - |
