# CodexTrace Results Summary

This generated summary consolidates the current paper-facing result tables.

## Pilots

| Pilot | Tasks | Runs | Failure outcomes | Main use |
| --- | ---: | ---: | ---: | --- |
| full30 | 30 | 60 | 0 | Process-waste analysis with saturated outcomes. |
| hard10 | 10 | 20 | 5 | Outcome-failure and hidden-grader analysis. |

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

## RQ2 Detector Boundary Result

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 5 | 0 | 0 | 0 |

Interpretation: the current deterministic process rules do not detect hidden semantic edge-case failures when the visible process trace looks clean.

## Claim-Evidence Shortlist

| Claim | Generated evidence |
| --- | --- |
| Intervention reduces process waste on full30. | `avg_repeated_tool_calls`, `avg_command_failures`, `avg_recover_events`, and `avg_token_usage` improve in the full30 table. |
| Intervention improves success on hard10. | hard10 `success_rate` improves from baseline to intervention. |
| Trace-only process rules have a semantic boundary. | hard10 label evaluation has 5 false negatives for `hidden_semantic_edge_case`. |
| Strong task oracles remain necessary. | hard10 failures are only visible through hidden graders, not process-rule findings. |
