# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

No failure tags were observed in these runs.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1 | 1 | 0 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 11.6 | 7.8 | -3.8 |
| avg_retry_count | 0.4667 | 0.2667 | -0.2 |
| avg_command_failures | 0.6667 | 0.2667 | -0.4 |
| avg_token_usage | 2.25e+05 | 1.908e+05 | -3.413e+04 |
| avg_failure_score | 3.333 | 1.333 | -2 |
| avg_recover_events | 2 | 0.6667 | -1.333 |
| avg_verify_events | 9.8 | 7.733 | -2.067 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=0, success=30, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 0 | 1 | 1 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 0 | 9.7 | 9.7 |
| retry_count | 0 | 0.3667 | 0.3667 |
| command_failure_count | 0 | 0.4667 | 0.4667 |
| token_usage | 0 | 2.079e+05 | 2.079e+05 |
| failure_score | 0 | 2.333 | 2.333 |
| turn_count | 0 | 1 | 1 |
| time_to_first_edit | 0 | 15.77 | 15.77 |
| time_to_first_test | 0 | 14.43 | 14.43 |
| phase_inspect_events | 0 | 9.333 | 9.333 |
| phase_edit_events | 0 | 3.833 | 3.833 |
| phase_verify_events | 0 | 8.767 | 8.767 |
| phase_recover_events | 0 | 1.333 | 1.333 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| CT-012 | baseline | success | 0 | - |
| CT-012 | intervention | success | 0 | - |
| CT-013 | baseline | success | 5 | - |
| CT-013 | intervention | success | 0 | - |
| CT-014 | baseline | success | 0 | - |
| CT-014 | intervention | success | 0 | - |
| CT-015 | baseline | success | 5 | - |
| CT-015 | intervention | success | 0 | - |
| CT-017 | baseline | success | 5 | - |
| CT-017 | intervention | success | 5 | - |
| CT-018 | baseline | success | 5 | - |
| CT-018 | intervention | success | 5 | - |
| CT-019 | baseline | success | 0 | - |
| CT-019 | intervention | success | 0 | - |
| CT-020 | baseline | success | 0 | - |
| CT-020 | intervention | success | 0 | - |
| CT-022 | baseline | success | 5 | - |
| CT-022 | intervention | success | 0 | - |
| CT-023 | baseline | success | 5 | - |
| CT-023 | intervention | success | 5 | - |
| CT-024 | baseline | success | 5 | - |
| CT-024 | intervention | success | 0 | - |
| CT-025 | baseline | success | 10 | - |
| CT-025 | intervention | success | 0 | - |
| CT-027 | baseline | success | 5 | - |
| CT-027 | intervention | success | 5 | - |
| CT-029 | baseline | success | 0 | - |
| CT-029 | intervention | success | 0 | - |
| CT-030 | baseline | success | 0 | - |
| CT-030 | intervention | success | 0 | - |
