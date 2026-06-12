# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

No failure tags were observed in these runs.

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1 | 1 | 0 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 7 | 6 | -1 |
| avg_retry_count | 0.3333 | 0 | -0.3333 |
| avg_command_failures | 0.3333 | 0 | -0.3333 |
| avg_token_usage | 1.727e+05 | 1.725e+05 | -210.3 |
| avg_failure_score | 1.667 | 0 | -1.667 |
| avg_recover_events | 0.3333 | 0 | -0.3333 |
| avg_verify_events | 2.667 | 2 | -0.6667 |

### Paired Task Summary

| Metric | Improved | Regressed | Unchanged | Average delta |
| --- | ---: | ---: | ---: | ---: |
| success | 0 | 0 | 3 | 0 |
| verification | 0 | 0 | 3 | 0 |
| repeated tool calls | 1 | 0 | 2 | -1 |
| token usage | 2 | 1 | 0 | -210.3 |
| failure score | 1 | 0 | 2 | -1.667 |

### Paired Task Deltas

| Task | Success delta | Verification delta | Repeated calls delta | Token delta | Failure score delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| PST-001 | 0 | 0 | 0 | 399 | 0 |
| PST-003 | 0 | 0 | -3 | -844 | -5 |
| PST-011 | 0 | 0 | 0 | -186 | 0 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=0, success=6, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 0 | 1 | 1 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 0 | 6.5 | 6.5 |
| retry_count | 0 | 0.1667 | 0.1667 |
| command_failure_count | 0 | 0.1667 | 0.1667 |
| token_usage | 0 | 1.726e+05 | 1.726e+05 |
| failure_score | 0 | 0.8333 | 0.8333 |
| turn_count | 0 | 1 | 1 |
| time_to_first_edit | 0 | 15 | 15 |
| time_to_first_test | 0 | 17.33 | 17.33 |
| phase_inspect_events | 0 | 11.5 | 11.5 |
| phase_edit_events | 0 | 3.667 | 3.667 |
| phase_verify_events | 0 | 2.333 | 2.333 |
| phase_recover_events | 0 | 0.1667 | 0.1667 |

## Per-Run Appendix

| Task | Prompt | Outcome | Failure score | Tags |
| --- | --- | --- | ---: | --- |
| PST-001 | baseline | success | 0 | - |
| PST-001 | intervention | success | 0 | - |
| PST-003 | baseline | success | 5 | - |
| PST-003 | intervention | success | 0 | - |
| PST-011 | baseline | success | 0 | - |
| PST-011 | intervention | success | 0 | - |
