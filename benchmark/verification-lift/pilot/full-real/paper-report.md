# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

No failure tags were observed in these runs.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.875 | 0.875 | 0 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 6.125 | 5.375 | -0.75 |
| avg_retry_count | 0 | 0 | 0 |
| avg_command_failures | 0 | 0 | 0 |
| avg_token_usage | 1.768e+05 | 1.722e+05 | -4662 |
| avg_failure_score | 0 | 0 | 0 |
| avg_recover_events | 0 | 0 | 0 |
| avg_verify_events | 2.625 | 2.125 | -0.5 |

### Paired Task Summary

| Metric | Improved | Regressed | Unchanged | Average delta |
| --- | ---: | ---: | ---: | ---: |
| success | 0 | 0 | 8 | 0 |
| verification | 0 | 0 | 8 | 0 |
| repeated tool calls | 5 | 1 | 2 | -0.75 |
| token usage | 5 | 3 | 0 | -4662 |
| failure score | 0 | 0 | 8 | 0 |

### Paired Task Deltas

| Task | Success delta | Verification delta | Repeated calls delta | Token delta | Failure score delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| VLT-001 | 0 | 0 | -1 | -585 | 0 |
| VLT-002 | 0 | 0 | -2 | -35147 | 0 |
| VLT-003 | 0 | 0 | 0 | 3 | 0 |
| VLT-004 | 0 | 0 | -2 | -231 | 0 |
| VLT-005 | 0 | 0 | 0 | 186 | 0 |
| VLT-006 | 0 | 0 | -1 | -1319 | 0 |
| VLT-007 | 0 | 0 | -1 | -989 | 0 |
| VLT-008 | 0 | 0 | 1 | 788 | 0 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=2, success=14, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1 | 1 | 0 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 6 | 5.714 | -0.2857 |
| retry_count | 0 | 0 | 0 |
| command_failure_count | 0 | 0 | 0 |
| token_usage | 1.903e+05 | 1.722e+05 | -1.809e+04 |
| failure_score | 0 | 0 | 0 |
| turn_count | 1 | 1 | 0 |
| time_to_first_edit | 13 | 14.29 | 1.286 |
| time_to_first_test | 16 | 17.29 | 1.286 |
| phase_inspect_events | 10 | 11.29 | 1.286 |
| phase_edit_events | 3 | 3 | 0 |
| phase_verify_events | 4.5 | 2.071 | -2.429 |
| phase_recover_events | 0 | 0 | 0 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| VLT-001 | baseline | success | 0 | - |
| VLT-001 | intervention | success | 0 | - |
| VLT-002 | baseline | failure | 0 | - |
| VLT-002 | intervention | failure | 0 | - |
| VLT-003 | baseline | success | 0 | - |
| VLT-003 | intervention | success | 0 | - |
| VLT-004 | baseline | success | 0 | - |
| VLT-004 | intervention | success | 0 | - |
| VLT-005 | baseline | success | 0 | - |
| VLT-005 | intervention | success | 0 | - |
| VLT-006 | baseline | success | 0 | - |
| VLT-006 | intervention | success | 0 | - |
| VLT-007 | baseline | success | 0 | - |
| VLT-007 | intervention | success | 0 | - |
| VLT-008 | baseline | success | 0 | - |
| VLT-008 | intervention | success | 0 | - |
