# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

No failure tags were observed in these runs.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.875 | 0.875 | 0 |
| verification_rate | 1 | 1 | 0 |
| success_check_verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 8.625 | 5.5 | -3.125 |
| avg_retry_count | 0 | 0 | 0 |
| avg_command_failures | 0 | 0 | 0 |
| avg_token_usage | 2.246e+05 | 1.855e+05 | -3.917e+04 |
| avg_failure_score | 0 | 0 | 0 |
| avg_recover_events | 0 | 0 | 0 |
| avg_verify_events | 5.875 | 2 | -3.875 |

### Paired Task Summary

| Metric | Improved | Regressed | Unchanged | Average delta |
| --- | ---: | ---: | ---: | ---: |
| success | 0 | 0 | 8 | 0 |
| verification | 0 | 0 | 8 | 0 |
| success check verification | 0 | 0 | 8 | 0 |
| repeated tool calls | 7 | 0 | 1 | -3.125 |
| token usage | 8 | 0 | 0 | -3.917e+04 |
| failure score | 0 | 0 | 8 | 0 |

### Paired Task Deltas

| Task | Success delta | Verification delta | Success-check verification delta | Repeated calls delta | Token delta | Failure score delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| VLV2-001 | 0 | 0 | 0 | -4 | -38723 | 0 |
| VLV2-002 | 0 | 0 | 0 | -3 | -38223 | 0 |
| VLV2-003 | 0 | 0 | 0 | -1 | -687 | 0 |
| VLV2-004 | 0 | 0 | 0 | -5 | -39904 | 0 |
| VLV2-005 | 0 | 0 | 0 | 0 | -28 | 0 |
| VLV2-006 | 0 | 0 | 0 | -3 | -77665 | 0 |
| VLV2-007 | 0 | 0 | 0 | -2 | -1146 | 0 |
| VLV2-008 | 0 | 0 | 0 | -7 | -116946 | 0 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=2, success=14, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1 | 1 | 0 |
| success_check_verification_rate | 1 | 1 | 0 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 6.5 | 7.143 | 0.6429 |
| retry_count | 0 | 0 | 0 |
| command_failure_count | 0 | 0 | 0 |
| token_usage | 2.051e+05 | 2.05e+05 | -23.57 |
| failure_score | 0 | 0 | 0 |
| turn_count | 1 | 1 | 0 |
| time_to_first_edit | 13 | 14.93 | 1.929 |
| time_to_first_test | 16 | 18.29 | 2.286 |
| phase_inspect_events | 10 | 11.93 | 1.929 |
| phase_edit_events | 3 | 3.286 | 0.2857 |
| phase_verify_events | 4.5 | 3.857 | -0.6429 |
| phase_recover_events | 0 | 0 | 0 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| VLV2-001 | baseline | success | 0 | - |
| VLV2-001 | intervention | success | 0 | - |
| VLV2-002 | baseline | failure | 0 | - |
| VLV2-002 | intervention | failure | 0 | - |
| VLV2-003 | baseline | success | 0 | - |
| VLV2-003 | intervention | success | 0 | - |
| VLV2-004 | baseline | success | 0 | - |
| VLV2-004 | intervention | success | 0 | - |
| VLV2-005 | baseline | success | 0 | - |
| VLV2-005 | intervention | success | 0 | - |
| VLV2-006 | baseline | success | 0 | - |
| VLV2-006 | intervention | success | 0 | - |
| VLV2-007 | baseline | success | 0 | - |
| VLV2-007 | intervention | success | 0 | - |
| VLV2-008 | baseline | success | 0 | - |
| VLV2-008 | intervention | success | 0 | - |
