# CodexTrace Results Summary

This generated summary consolidates the current paper-facing result tables.

## Pilots

| Pilot | Tasks | Runs | Failure outcomes | Main use |
| --- | ---: | ---: | ---: | --- |
| full30 | 30 | 60 | 0 | Process-waste analysis with saturated outcomes. |
| hard10 | 10 | 20 | 5 | Outcome-failure and hidden-grader analysis. |
| hard30 | 30 | 60 | 30 | Submission-ready hard-tier hidden-grader artifact. |
| process-stress | 12 | 24 | 2 | Failure-mode stress tasks with real Codex traces. |
| verification-lift | 8 | 16 | 2 | Targeted verification-rate stress prompt contrast. |
| verification-ablation | 4 | 8 | 2 | Auxiliary no-verify baseline ablation, not an ordinary baseline. |

## RQ3 Baseline vs Intervention

### Full30 Seed Pilot

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 1.00 | 1.00 | 0.00 |
| verification_rate | 1.00 | 1.00 | 0.00 |
| success_check_verification_rate | 1.00 | 1.00 | 0.00 |
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
| success_check_verification_rate | 1.00 | 1.00 | 0.00 |
| avg_repeated_tool_calls | 9.2 | 6.2 | -3 |
| avg_token_usage | 248.9k | 187.5k | -61.4k |
| avg_verify_events | 7.3 | 3.7 | -3.6 |

### Hard30 Pilot

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.50 | 0.50 | 0.00 |
| verification_rate | 1.00 | 1.00 | 0.00 |
| success_check_verification_rate | 1.00 | 1.00 | 0.00 |
| avg_repeated_tool_calls | 12.93 | 9.2 | -3.733 |
| avg_command_failures | 0.3 | 0.1 | -0.2 |
| avg_token_usage | 355.0k | 256.3k | -98.7k |
| avg_failure_score | 3.5 | 1.167 | -2.333 |

Paired hard30 deltas: token usage improves in 26/30 tasks, repeated tool calls improve in 26/30 tasks, success improves in 1 task(s) and regresses in 1 task(s).

### Process-Stress Pilot

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.92 | 0.92 | 0.00 |
| verification_rate | 1.00 | 1.00 | 0.00 |
| success_check_verification_rate | 1.00 | 1.00 | 0.00 |
| avg_repeated_tool_calls | 8.083 | 7.167 | -0.9166 |
| avg_recover_events | 1.25 | 0.8333 | -0.4167 |
| avg_token_usage | 209.0k | 185.1k | -23.9k |
| avg_failure_score | 1.25 | 1.25 | 0 |

Paired process-stress deltas: token usage improves in 5/12 tasks, repeated tool calls improve in 4/12 tasks, success improves in 0 task(s) and regresses in 0 task(s).

### Verification-Lift Pilot

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.88 | 0.88 | 0.00 |
| verification_rate | 1.00 | 1.00 | 0.00 |
| success_check_verification_rate | 1.00 | 1.00 | 0.00 |
| avg_repeated_tool_calls | 6.125 | 5.375 | -0.75 |
| avg_verify_events | 2.625 | 2.125 | -0.5 |
| avg_token_usage | 176.8k | 172.2k | -4.7k |
| avg_failure_score | 0 | 0 | 0 |

Paired verification-lift deltas: verification improves in 0/8 tasks, exact success-check verification improves in 0/8 tasks, token usage improves in 5/8 tasks, repeated tool calls improve in 5/8 tasks.

### Verification Ablation Pilot

This auxiliary pilot uses an explicit no-verification baseline and should not be interpreted as the ordinary Codex baseline.

| Metric | Baseline | Intervention | Delta |
| --- | ---: | ---: | ---: |
| success_rate | 0.75 | 0.75 | 0.00 |
| verification_rate | 0.00 | 1.00 | 1.00 |
| success_check_verification_rate | 0.00 | 1.00 | 1.00 |
| avg_repeated_tool_calls | 4 | 5.25 | 1.25 |
| avg_verify_events | 0 | 2 | 2 |
| avg_token_usage | 145.8k | 172.1k | 26.3k |
| avg_failure_score | 61.25 | 0 | -61.25 |

Paired verification-ablation deltas: verification improves in 4/4 tasks, exact success-check verification improves in 4/4 tasks, and failure score improves in 4/4 tasks.

## RQ2 Detector Boundary Result

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 30 | 0 | 0 | 0 |
| repetitive_exploration | 4 | 0 | 0 | 1 | 1 | 1 |

Interpretation: deterministic process rules detect high-volume `repetitive_exploration` positives, but still do not detect hidden semantic edge-case failures when the visible process trace looks clean.

### Controlled Detector Fixture Check

These minimal JSONL traces are rule-level fixtures, not real Codex pilot runs. They cover 6 process labels with micro-F1 1.

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| context_drift | 1 | 0 | 0 | 1 | 1 | 1 |
| premature_completion | 1 | 0 | 0 | 1 | 1 | 1 |
| repetitive_exploration | 1 | 0 | 0 | 1 | 1 | 1 |
| sandbox_permission_deadlock | 1 | 0 | 0 | 1 | 1 | 1 |
| unrecovered_tool_error | 2 | 0 | 0 | 1 | 1 | 1 |
| verification_gap | 2 | 0 | 0 | 1 | 1 | 1 |

### Full30 Process-Positive Detector Check

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| repetitive_exploration | 0 | 2 | 0 | 0 | 0 | 0 |
| sandbox_permission_deadlock | 1 | 0 | 0 | 1 | 1 | 1 |

Interpretation: full30 adds an observed sandbox/permission process positive, while also exposing repetitive-exploration false positives in the process-label slice.

### Process-Stress Detector Boundary Check

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 2 | 0 | 0 | 0 |

Interpretation: the process-stress pilot repeats the same boundary: both failed runs are hidden semantic edge cases, producing 2 trace-only false negatives.

### Verification-Lift Detector Boundary Check

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 2 | 0 | 0 | 0 |

Interpretation: the targeted verification-lift pilot still has saturated verification and 2 hidden semantic false negatives.

### Verification Ablation Detector Check

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 2 | 0 | 0 | 0 |
| premature_completion | 3 | 0 | 0 | 1 | 1 | 1 |
| verification_gap | 4 | 0 | 0 | 1 | 1 | 1 |

Interpretation: explicit no-verify ablation creates detectable verification gaps, while hidden semantic failures remain outside process-rule detection.

## RQ4 Trace Signals By Outcome

Hard30 outcome failures are hidden semantic edge cases, so most process signals do not separate failures from successes.

| Signal | Failure mean | Success mean | Delta success-failure |
| --- | ---: | ---: | ---: |
| verification_rate | 1.00 | 1.00 | 0.00 |
| success_check_verification_rate | 1.00 | 1.00 | 0.00 |
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
| Process-stress intervention reduces token and repeated-call waste while success stays flat. | process-stress keeps success at 91.67% while reducing repeated tool calls and token usage. |
| Verification-lift stress test does not support a verification-rate lift. | verification-lift verification remains 100% -> 100%, while repeated calls and token usage fall slightly. |
| Trace-only process rules have a semantic boundary. | hard30 label evaluation has 30 false negatives for `hidden_semantic_edge_case`, while detecting observed process positives such as `repetitive_exploration`. |
| RQ4 signal analysis explains the detector boundary. | hard30 `verification_rate` and `unresolved_error` are equal for successful and failed runs. |
| Strong task oracles remain necessary. | hard-tier failures are only visible through hidden graders, not process-rule findings. |
