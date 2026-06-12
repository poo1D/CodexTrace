# CodexTrace Research Aggregate

## Summary

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.5 | 0.5 | 0 |
| verification_rate | 1 | 1 | 0 |
| success_check_verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 12.93 | 9.2 | -3.733 |
| avg_retry_count | 0.2 | 0 | -0.2 |
| avg_command_failures | 0.3 | 0.1 | -0.2 |
| avg_recover_events | 1.2 | 0.8333 | -0.3667 |
| avg_verify_events | 10.7 | 6.767 | -3.933 |
| avg_token_usage | 3.55e+05 | 2.563e+05 | -9.866e+04 |
| avg_failure_score | 3.5 | 1.167 | -2.333 |

## Runs

| Task | Prompt | Outcome | Failure score | Findings |
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
| HARD-011 | baseline | success | 30 | repeated_search_or_read |
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
| HARD-033 | baseline | failure | 35 | repeated_search_or_read |
| HARD-033 | intervention | failure | 0 | - |
| HARD-035 | baseline | failure | 0 | - |
| HARD-035 | intervention | failure | 0 | - |
| HARD-038 | baseline | failure | 0 | - |
| HARD-038 | intervention | failure | 0 | - |
| HARD-039 | baseline | success | 25 | repeated_search_or_read |
| HARD-039 | intervention | success | 25 | repeated_search_or_read |
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
