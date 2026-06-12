# CodexTrace Research Aggregate

## Summary

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.75 | 0.75 | 0 |
| verification_rate | 0 | 1 | 1 |
| success_check_verification_rate | 0 | 1 | 1 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 4 | 5.25 | 1.25 |
| avg_retry_count | 0 | 0 | 0 |
| avg_command_failures | 0 | 0 | 0 |
| avg_recover_events | 0 | 0 | 0 |
| avg_verify_events | 0 | 2 | 2 |
| avg_token_usage | 1.458e+05 | 1.721e+05 | 2.632e+04 |
| avg_failure_score | 61.25 | 0 | -61.25 |

## Runs

| Task | Prompt | Outcome | Failure score | Findings |
| --- | --- | --- | ---: | --- |
| VAB-001 | baseline | success | 70 | verification_gap, premature_completion |
| VAB-001 | intervention | success | 0 | - |
| VAB-002 | baseline | failure | 70 | verification_gap, premature_completion |
| VAB-002 | intervention | failure | 0 | - |
| VAB-003 | baseline | success | 35 | verification_gap |
| VAB-003 | intervention | success | 0 | - |
| VAB-004 | baseline | success | 70 | verification_gap, premature_completion |
| VAB-004 | intervention | success | 0 | - |
