# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

| Failure tag | Count | Percentage | Example task |
| --- | ---: | ---: | --- |
| sandbox_permission_deadlock | 1 | 100 | CT-021/baseline |

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1 | 1 | 0 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 10.43 | 6.429 | -4 |
| avg_retry_count | 0.1429 | 0.2857 | 0.1428 |
| avg_command_failures | 0.7143 | 0.2857 | -0.4286 |
| avg_token_usage | 2.342e+05 | 1.826e+05 | -5.164e+04 |
| avg_failure_score | 5 | 1.429 | -3.571 |
| avg_recover_events | 4.571 | 0.2857 | -4.286 |
| avg_verify_events | 6.857 | 4.429 | -2.428 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=0, success=14, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 0 | 1 | 1 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 0 | 8.429 | 8.429 |
| retry_count | 0 | 0.2143 | 0.2143 |
| command_failure_count | 0 | 0.5 | 0.5 |
| token_usage | 0 | 2.084e+05 | 2.084e+05 |
| failure_score | 0 | 3.214 | 3.214 |
| turn_count | 0 | 1 | 1 |
| time_to_first_edit | 0 | 14.71 | 14.71 |
| time_to_first_test | 0 | 15.86 | 15.86 |
| phase_inspect_events | 0 | 10.71 | 10.71 |
| phase_edit_events | 0 | 3.071 | 3.071 |
| phase_verify_events | 0 | 5.643 | 5.643 |
| phase_recover_events | 0 | 2.429 | 2.429 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| CT-001 | baseline | success | 0 | - |
| CT-001 | intervention | success | 0 | - |
| CT-006 | baseline | success | 0 | - |
| CT-006 | intervention | success | 0 | - |
| CT-011 | baseline | success | 0 | - |
| CT-011 | intervention | success | 0 | - |
| CT-016 | baseline | success | 0 | - |
| CT-016 | intervention | success | 0 | - |
| CT-021 | baseline | success | 35 | sandbox_permission_deadlock |
| CT-021 | intervention | success | 0 | - |
| CT-026 | baseline | success | 0 | - |
| CT-026 | intervention | success | 10 | - |
| CT-028 | baseline | success | 0 | - |
| CT-028 | intervention | success | 0 | - |
