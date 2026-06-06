# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

No failure tags were observed in these runs.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1 | 1 | 0 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 8.25 | 6 | -2.25 |
| avg_retry_count | 0 | 0 | 0 |
| avg_command_failures | 0 | 0 | 0 |
| avg_token_usage | 1.936e+05 | 1.754e+05 | -1.818e+04 |
| avg_failure_score | 0 | 0 | 0 |
| avg_recover_events | 0 | 0 | 0 |
| avg_verify_events | 6.375 | 3.125 | -3.25 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=0, success=16, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 0 | 1 | 1 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 0 | 7.125 | 7.125 |
| retry_count | 0 | 0 | 0 |
| command_failure_count | 0 | 0 | 0 |
| token_usage | 0 | 1.845e+05 | 1.845e+05 |
| failure_score | 0 | 0 | 0 |
| turn_count | 0 | 1 | 1 |
| time_to_first_edit | 0 | 15.06 | 15.06 |
| time_to_first_test | 0 | 17.44 | 17.44 |
| phase_inspect_events | 0 | 10.56 | 10.56 |
| phase_edit_events | 0 | 3.5 | 3.5 |
| phase_verify_events | 0 | 4.75 | 4.75 |
| phase_recover_events | 0 | 0 | 0 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| CT-002 | baseline | success | 0 | - |
| CT-002 | intervention | success | 0 | - |
| CT-003 | baseline | success | 0 | - |
| CT-003 | intervention | success | 0 | - |
| CT-004 | baseline | success | 0 | - |
| CT-004 | intervention | success | 0 | - |
| CT-005 | baseline | success | 0 | - |
| CT-005 | intervention | success | 0 | - |
| CT-007 | baseline | success | 0 | - |
| CT-007 | intervention | success | 0 | - |
| CT-008 | baseline | success | 0 | - |
| CT-008 | intervention | success | 0 | - |
| CT-009 | baseline | success | 0 | - |
| CT-009 | intervention | success | 0 | - |
| CT-010 | baseline | success | 0 | - |
| CT-010 | intervention | success | 0 | - |
