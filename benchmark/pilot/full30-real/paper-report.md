# CodexTrace Paper Tables

## RQ1 Failure Taxonomy Distribution

| Failure tag | Count | Percentage | Example task |
| --- | ---: | ---: | --- |
| repetitive_exploration | 2 | 66.67 | CT-021/baseline |
| sandbox_permission_deadlock | 1 | 33.33 | CT-021/baseline |

## RQ3 Baseline vs Intervention

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1 | 1 | 0 |
| verification_rate | 1 | 1 | 0 |
| success_check_verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 10.43 | 7 | -3.433 |
| avg_retry_count | 0.2667 | 0.2 | -0.0667 |
| avg_command_failures | 0.5 | 0.2 | -0.3 |
| avg_token_usage | 2.187e+05 | 1.848e+05 | -3.396e+04 |
| avg_failure_score | 4.167 | 1 | -3.167 |
| avg_recover_events | 2.067 | 0.4 | -1.667 |
| avg_verify_events | 8.2 | 5.733 | -2.467 |

### Paired Task Summary

| Metric | Improved | Regressed | Unchanged | Average delta |
| --- | ---: | ---: | ---: | ---: |
| success | 0 | 0 | 30 | 0 |
| verification | 0 | 0 | 30 | 0 |
| success check verification | 0 | 0 | 30 | 0 |
| repeated tool calls | 24 | 1 | 5 | -3.433 |
| token usage | 19 | 11 | 0 | -3.396e+04 |
| failure score | 7 | 1 | 22 | -3.167 |

### Paired Task Deltas

| Task | Success delta | Verification delta | Success-check verification delta | Repeated calls delta | Token delta | Failure score delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CT-001 | 0 | 0 | 0 | -1 | -309 | 0 |
| CT-002 | 0 | 0 | 0 | -1 | 32908 | 0 |
| CT-003 | 0 | 0 | 0 | -3 | -737 | 0 |
| CT-004 | 0 | 0 | 0 | -2 | -195 | 0 |
| CT-005 | 0 | 0 | 0 | -3 | -34564 | 0 |
| CT-006 | 0 | 0 | 0 | -1 | 1 | 0 |
| CT-007 | 0 | 0 | 0 | -7 | -175275 | 0 |
| CT-008 | 0 | 0 | 0 | 0 | 33390 | 0 |
| CT-009 | 0 | 0 | 0 | -2 | -34678 | 0 |
| CT-010 | 0 | 0 | 0 | 0 | 33700 | 0 |
| CT-011 | 0 | 0 | 0 | 2 | 34936 | 0 |
| CT-012 | 0 | 0 | 0 | 0 | 45 | 0 |
| CT-013 | 0 | 0 | 0 | -2 | 249 | -5 |
| CT-014 | 0 | 0 | 0 | -4 | -33053 | 0 |
| CT-015 | 0 | 0 | 0 | -8 | -66703 | -5 |
| CT-016 | 0 | 0 | 0 | -2 | -327 | 0 |
| CT-017 | 0 | 0 | 0 | -2 | -605 | 0 |
| CT-018 | 0 | 0 | 0 | -4 | -34162 | 0 |
| CT-019 | 0 | 0 | 0 | -4 | -33038 | 0 |
| CT-020 | 0 | 0 | 0 | -2 | -431 | 0 |
| CT-021 | 0 | 0 | 0 | -19 | -366125 | -55 |
| CT-022 | 0 | 0 | 0 | -2 | 226 | -5 |
| CT-023 | 0 | 0 | 0 | -4 | -35246 | 0 |
| CT-024 | 0 | 0 | 0 | -3 | 88 | -5 |
| CT-025 | 0 | 0 | 0 | -5 | -66655 | -10 |
| CT-026 | 0 | 0 | 0 | -7 | -30410 | 10 |
| CT-027 | 0 | 0 | 0 | -1 | 256 | 0 |
| CT-028 | 0 | 0 | 0 | 0 | 780 | 0 |
| CT-029 | 0 | 0 | 0 | 0 | -34598 | 0 |
| CT-030 | 0 | 0 | 0 | -16 | -208363 | -20 |

## RQ4 Trace Signals By Outcome

Outcome counts: failure=0, success=60, unknown=0.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 0 | 1 | 1 |
| success_check_verification_rate | 0 | 1 | 1 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 0 | 8.717 | 8.717 |
| retry_count | 0 | 0.2333 | 0.2333 |
| command_failure_count | 0 | 0.35 | 0.35 |
| token_usage | 0 | 2.018e+05 | 2.018e+05 |
| failure_score | 0 | 2.583 | 2.583 |
| turn_count | 0 | 1 | 1 |
| time_to_first_edit | 0 | 15.33 | 15.33 |
| time_to_first_test | 0 | 15.57 | 15.57 |
| phase_inspect_events | 0 | 9.983 | 9.983 |
| phase_edit_events | 0 | 3.567 | 3.567 |
| phase_verify_events | 0 | 6.967 | 6.967 |
| phase_recover_events | 0 | 1.233 | 1.233 |

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
| CT-021 | baseline | success | 55 | repetitive_exploration, sandbox_permission_deadlock |
| CT-021 | intervention | success | 0 | - |
| CT-026 | baseline | success | 0 | - |
| CT-026 | intervention | success | 10 | - |
| CT-028 | baseline | success | 0 | - |
| CT-028 | intervention | success | 0 | - |
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
| CT-030 | baseline | success | 20 | repetitive_exploration |
| CT-030 | intervention | success | 0 | - |
