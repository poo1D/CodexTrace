# CodexTrace Research Aggregate

## Summary

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1 | 1 | 0 |
| verification_rate | 1 | 1 | 0 |
| unresolved_error_rate | 0 | 0 | 0 |
| avg_repeated_tool_calls | 10.43 | 6.429 | -4 |
| avg_retry_count | 0.1429 | 0.2857 | 0.1428 |
| avg_command_failures | 0.7143 | 0.2857 | -0.4286 |
| avg_recover_events | 4.571 | 0.2857 | -4.286 |
| avg_verify_events | 6.857 | 4.429 | -2.428 |
| avg_token_usage | 2.342e+05 | 1.826e+05 | -5.164e+04 |
| avg_failure_score | 5 | 1.429 | -3.571 |

## Runs

| Task | Prompt | Outcome | Failure score | Findings |
| --- | --- | --- | ---: | --- |
| CT-001 | baseline | success | 0 | - |
| CT-001 | intervention | success | 0 | - |
| CT-006 | baseline | success | 0 | - |
| CT-006 | intervention | success | 0 | - |
| CT-011 | baseline | success | 0 | - |
| CT-011 | intervention | success | 0 | - |
| CT-016 | baseline | success | 0 | - |
| CT-016 | intervention | success | 0 | - |
| CT-021 | baseline | success | 35 | sandbox_or_permission_block |
| CT-021 | intervention | success | 0 | - |
| CT-026 | baseline | success | 0 | - |
| CT-026 | intervention | success | 10 | - |
| CT-028 | baseline | success | 0 | - |
| CT-028 | intervention | success | 0 | - |
