# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

No failure tags were observed in these runs.

## RQ2 Detector Agreement

No detector labels were present to score.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1 | 1 | 0 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 6.333 | 6.667 | 0.3334 |
| avg_retry_count | 0 | 0.3333 | 0.3333 |
| avg_command_failures | 0 | 0.3333 | 0.3333 |
| avg_token_usage | 9.425e+04 | 1.085e+05 | 1.421e+04 |
| avg_failure_score | 0 | 1.667 | 1.667 |
| avg_recover_events | 0 | 0.3333 | 0.3333 |
| avg_verify_events | 2 | 6 | 4 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=0, success=6, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 0 | 1 | 1 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 0 | 6.5 | 6.5 |
| retry_count | 0 | 0.1667 | 0.1667 |
| command_failure_count | 0 | 0.1667 | 0.1667 |
| token_usage | 0 | 1.014e+05 | 1.014e+05 |
| failure_score | 0 | 0.8333 | 0.8333 |
| turn_count | 0 | 1 | 1 |
| time_to_first_edit | 0 | 15 | 15 |
| time_to_first_test | 0 | 16.17 | 16.17 |
| phase_inspect_events | 0 | 10.33 | 10.33 |
| phase_edit_events | 0 | 3.833 | 3.833 |
| phase_verify_events | 0 | 4 | 4 |
| phase_recover_events | 0 | 0.1667 | 0.1667 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| SM-001 | baseline | success | 0 | - |
| SM-001 | intervention | success | 0 | - |
| SM-002 | baseline | success | 0 | - |
| SM-002 | intervention | success | 0 | - |
| SM-003 | baseline | success | 0 | - |
| SM-003 | intervention | success | 5 | - |
