# CodexTrace Results Summary

This generated summary consolidates the current paper-facing result tables.

## Pilots

| Pilot | Tasks | Runs | Failure outcomes | Main use |
| --- | ---: | ---: | ---: | --- |
| full30 | 30 | 60 | 0 | Process-waste analysis with saturated outcomes. |
| hard10 | 10 | 20 | 5 | Outcome-failure and hidden-grader analysis. |
| hard30 | 30 | 60 | 30 | Submission-ready hard-tier hidden-grader artifact. |

## RQ3 Baseline vs Intervention

### Full30 Seed Pilot

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1.00 | 1.00 | 0.00 |
| avg_repeated_tool_calls | 10.43 | 7 | -3.433 |
| avg_command_failures | 0.5 | 0.2 | -0.3 |
| avg_recover_events | 2.067 | 0.4 | -1.667 |
| avg_token_usage | 218.7k | 184.8k | -34.0k |
| avg_failure_score | 2.833 | 1 | -1.833 |

### Hard10 Pilot

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.70 | 0.80 | 0.10 |
| verification_rate | 1.00 | 1.00 | 0.00 |
| avg_repeated_tool_calls | 9.2 | 6.2 | -3 |
| avg_token_usage | 248.9k | 187.5k | -61.4k |
| avg_verify_events | 7.3 | 3.7 | -3.6 |

### Hard30 Pilot

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.50 | 0.50 | 0.00 |
| verification_rate | 1.00 | 1.00 | 0.00 |
| avg_repeated_tool_calls | 12.93 | 9.20 | -3.73 |
| avg_command_failures | 0.30 | 0.10 | -0.20 |
| avg_token_usage | 355.0k | 256.3k | -98.7k |
| avg_failure_score | 1.50 | 0.50 | -1.00 |

Paired hard30 deltas: token usage improves in 26/30 tasks, repeated tool calls
improve in 26/30 tasks, success improves in one task and regresses in one task.

## RQ2 Detector Boundary Result

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 30 | 0 | 0 | 0 |

Interpretation: the current deterministic process rules do not detect hidden semantic edge-case failures when the visible process trace looks clean.

## RQ4 Trace Signals By Outcome

Hard30 outcome failures are hidden semantic edge cases, so most process signals do not separate failures from successes.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1.00 | 1.00 | 0.00 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 10.8 | 11.33 | 0.53 |
| retry_count | 0.13 | 0.07 | -0.07 |
| command_failure_count | 0.23 | 0.17 | -0.07 |
| token_usage | 306.5k | 304.8k | -1.8k |
| failure_score | 1.17 | 0.83 | -0.33 |
| turn_count | 1 | 1 | 0 |
| time_to_first_edit | 15.6 | 15.97 | 0.37 |
| time_to_first_test | 19.27 | 20.3 | 1.03 |
| phase_inspect_events | 12.37 | 12.83 | 0.47 |
| phase_edit_events | 7.13 | 6.50 | -0.63 |
| phase_verify_events | 8.17 | 9.30 | 1.13 |
| phase_recover_events | 1.23 | 0.80 | -0.43 |

Interpretation: `verification_rate` and `unresolved_error` are identical across
hard30 successes and failures, and the remaining process signals separate them
only weakly. The visible traces often look procedurally clean; hidden graders
reveal the missed semantic edge cases.

## Claim-Evidence Shortlist

| Claim | Generated evidence |
| --- | --- |
| Intervention reduces process waste on full30. | `avg_repeated_tool_calls`, `avg_command_failures`, `avg_recover_events`, and `avg_token_usage` improve in the full30 table. |
| Intervention improves success on hard10. | hard10 `success_rate` improves from baseline to intervention. |
| Intervention reduces waste on hard30. | hard30 repeated tool calls, command failures, token usage, and failure score improve. |
| Trace-only process rules have a semantic boundary. | hard30 label evaluation has 30 false negatives for `hidden_semantic_edge_case`. |
| RQ4 signal analysis explains the detector boundary. | hard30 `verification_rate` and `unresolved_error` are equal for successful and failed runs. |
| Strong task oracles remain necessary. | hard10 failures are only visible through hidden graders, not process-rule findings. |
