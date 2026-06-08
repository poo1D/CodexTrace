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
| avg_failure_score | 4.167 | 1 | -3.167 |

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
| avg_repeated_tool_calls | 12.93 | 9.2 | -3.733 |
| avg_command_failures | 0.3 | 0.1 | -0.2 |
| avg_token_usage | 355.0k | 256.3k | -98.7k |
| avg_failure_score | 3.5 | 1.167 | -2.333 |

Paired hard30 deltas: token usage improves in 26/30 tasks, repeated tool calls improve in 26/30 tasks, success improves in 1 task(s) and regresses in 1 task(s).

## RQ2 Detector Boundary Result

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 30 | 0 | 0 | 0 |
| repetitive_exploration | 4 | 0 | 0 | 1 | 1 | 1 |

Interpretation: deterministic process rules detect high-volume `repetitive_exploration` positives, but still do not detect hidden semantic edge-case failures when the visible process trace looks clean.

## RQ4 Trace Signals By Outcome

Hard30 outcome failures are hidden semantic edge cases, so most process signals do not separate failures from successes.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1.00 | 1.00 | 0.00 |
| unresolved_error | 0 | 0 | 0 |
| repeated_tool_call_count | 10.8 | 11.33 | 0.5333 |
| retry_count | 0.1333 | 0.0667 | -0.0666 |
| command_failure_count | 0.2333 | 0.1667 | -0.0666 |
| token_usage | 306.5k | 304.8k | -1.8k |
| failure_score | 1.833 | 2.833 | 1 |
| turn_count | 1 | 1 | 0 |
| time_to_first_edit | 15.6 | 15.97 | 0.3667 |
| time_to_first_test | 19.27 | 20.3 | 1.033 |
| phase_inspect_events | 12.37 | 12.83 | 0.4666 |
| phase_edit_events | 7.133 | 6.5 | -0.6333 |
| phase_verify_events | 8.167 | 9.3 | 1.133 |
| phase_recover_events | 1.233 | 0.8 | -0.4333 |

Interpretation: `verification_rate` and `unresolved_error` do not separate hidden semantic failures from successes. The visible traces often look procedurally clean; hidden graders reveal the missed semantic edge cases.

## Claim-Evidence Shortlist

| Claim | Generated evidence |
| --- | --- |
| Intervention reduces process waste on full30. | `avg_repeated_tool_calls`, `avg_command_failures`, `avg_recover_events`, and `avg_token_usage` improve in the full30 table. |
| Intervention improves success on hard10. | hard10 `success_rate` improves from baseline to intervention. |
| Intervention reduces waste on hard30. | hard30 repeated tool calls, command failures, token usage, and failure score improve. |
| Trace-only process rules have a semantic boundary. | hard30 label evaluation has 30 false negatives for `hidden_semantic_edge_case`, while detecting observed process positives such as `repetitive_exploration`. |
| RQ4 signal analysis explains the detector boundary. | hard30 `verification_rate` and `unresolved_error` are equal for successful and failed runs. |
| Strong task oracles remain necessary. | hard-tier failures are only visible through hidden graders, not process-rule findings. |
