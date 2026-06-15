# Metric Coverage Audit

This generated audit checks that the metrics named in the experiment design are collected at run level, summarized for baseline/intervention comparison, emitted to CSV, and visible in generated aggregate Markdown.

## Summary

- Ready: yes
- Manifests checked: 7 / 7
- Metrics covered: 11 / 11
- Coverage cells covered: 77 / 77
- Nullable metrics checked: 2
- Nullable manifest cells with observations: 14 / 14

## Manifests

| Manifest | Metrics covered | Ready |
| --- | ---: | --- |
| `benchmark/pilot/full30-real/runs.jsonl` | 11 / 11 | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | 11 / 11 | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | 11 / 11 | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | 11 / 11 | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | 11 / 11 | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | 11 / 11 | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | 11 / 11 | yes |

## Coverage

| Manifest | Metric | Run key | Summary key | CSV | Markdown | Covered |
| --- | --- | --- | --- | --- | --- | --- |
| `benchmark/pilot/full30-real/runs.jsonl` | success_rate | `success` yes | `success_rate` yes | yes | yes | yes |
| `benchmark/pilot/full30-real/runs.jsonl` | verification_rate | `verification_rate` yes | `verification_rate` yes | yes | yes | yes |
| `benchmark/pilot/full30-real/runs.jsonl` | unresolved_error_rate | `unresolved_error` yes | `unresolved_error_rate` yes | yes | yes | yes |
| `benchmark/pilot/full30-real/runs.jsonl` | repeated_tool_call_count | `repeated_tool_call_count` yes | `avg_repeated_tool_calls` yes | yes | yes | yes |
| `benchmark/pilot/full30-real/runs.jsonl` | retry_count | `retry_count` yes | `avg_retry_count` yes | yes | yes | yes |
| `benchmark/pilot/full30-real/runs.jsonl` | turn_count | `turn_count` yes | `avg_turn_count` yes | yes | yes | yes |
| `benchmark/pilot/full30-real/runs.jsonl` | token_usage | `token_usage` yes | `avg_token_usage` yes | yes | yes | yes |
| `benchmark/pilot/full30-real/runs.jsonl` | command_failure_count | `command_failure_count` yes | `avg_command_failures` yes | yes | yes | yes |
| `benchmark/pilot/full30-real/runs.jsonl` | time_to_first_edit | `time_to_first_edit` yes | `avg_time_to_first_edit` yes | yes | yes | yes |
| `benchmark/pilot/full30-real/runs.jsonl` | time_to_first_test | `time_to_first_test` yes | `avg_time_to_first_test` yes | yes | yes | yes |
| `benchmark/pilot/full30-real/runs.jsonl` | failure_score | `failure_score` yes | `avg_failure_score` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | success_rate | `success` yes | `success_rate` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | verification_rate | `verification_rate` yes | `verification_rate` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | unresolved_error_rate | `unresolved_error` yes | `unresolved_error_rate` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | repeated_tool_call_count | `repeated_tool_call_count` yes | `avg_repeated_tool_calls` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | retry_count | `retry_count` yes | `avg_retry_count` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | turn_count | `turn_count` yes | `avg_turn_count` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | token_usage | `token_usage` yes | `avg_token_usage` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | command_failure_count | `command_failure_count` yes | `avg_command_failures` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | time_to_first_edit | `time_to_first_edit` yes | `avg_time_to_first_edit` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | time_to_first_test | `time_to_first_test` yes | `avg_time_to_first_test` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | failure_score | `failure_score` yes | `avg_failure_score` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | success_rate | `success` yes | `success_rate` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | verification_rate | `verification_rate` yes | `verification_rate` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | unresolved_error_rate | `unresolved_error` yes | `unresolved_error_rate` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | repeated_tool_call_count | `repeated_tool_call_count` yes | `avg_repeated_tool_calls` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | retry_count | `retry_count` yes | `avg_retry_count` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | turn_count | `turn_count` yes | `avg_turn_count` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | token_usage | `token_usage` yes | `avg_token_usage` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | command_failure_count | `command_failure_count` yes | `avg_command_failures` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | time_to_first_edit | `time_to_first_edit` yes | `avg_time_to_first_edit` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | time_to_first_test | `time_to_first_test` yes | `avg_time_to_first_test` yes | yes | yes | yes |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | failure_score | `failure_score` yes | `avg_failure_score` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | success_rate | `success` yes | `success_rate` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | verification_rate | `verification_rate` yes | `verification_rate` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | unresolved_error_rate | `unresolved_error` yes | `unresolved_error_rate` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | repeated_tool_call_count | `repeated_tool_call_count` yes | `avg_repeated_tool_calls` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | retry_count | `retry_count` yes | `avg_retry_count` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | turn_count | `turn_count` yes | `avg_turn_count` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | token_usage | `token_usage` yes | `avg_token_usage` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | command_failure_count | `command_failure_count` yes | `avg_command_failures` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | time_to_first_edit | `time_to_first_edit` yes | `avg_time_to_first_edit` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | time_to_first_test | `time_to_first_test` yes | `avg_time_to_first_test` yes | yes | yes | yes |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | failure_score | `failure_score` yes | `avg_failure_score` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | success_rate | `success` yes | `success_rate` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | verification_rate | `verification_rate` yes | `verification_rate` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | unresolved_error_rate | `unresolved_error` yes | `unresolved_error_rate` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | repeated_tool_call_count | `repeated_tool_call_count` yes | `avg_repeated_tool_calls` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | retry_count | `retry_count` yes | `avg_retry_count` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | turn_count | `turn_count` yes | `avg_turn_count` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | token_usage | `token_usage` yes | `avg_token_usage` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | command_failure_count | `command_failure_count` yes | `avg_command_failures` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | time_to_first_edit | `time_to_first_edit` yes | `avg_time_to_first_edit` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | time_to_first_test | `time_to_first_test` yes | `avg_time_to_first_test` yes | yes | yes | yes |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | failure_score | `failure_score` yes | `avg_failure_score` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | success_rate | `success` yes | `success_rate` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | verification_rate | `verification_rate` yes | `verification_rate` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | unresolved_error_rate | `unresolved_error` yes | `unresolved_error_rate` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | repeated_tool_call_count | `repeated_tool_call_count` yes | `avg_repeated_tool_calls` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | retry_count | `retry_count` yes | `avg_retry_count` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | turn_count | `turn_count` yes | `avg_turn_count` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | token_usage | `token_usage` yes | `avg_token_usage` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | command_failure_count | `command_failure_count` yes | `avg_command_failures` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | time_to_first_edit | `time_to_first_edit` yes | `avg_time_to_first_edit` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | time_to_first_test | `time_to_first_test` yes | `avg_time_to_first_test` yes | yes | yes | yes |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | failure_score | `failure_score` yes | `avg_failure_score` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | success_rate | `success` yes | `success_rate` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | verification_rate | `verification_rate` yes | `verification_rate` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | unresolved_error_rate | `unresolved_error` yes | `unresolved_error_rate` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | repeated_tool_call_count | `repeated_tool_call_count` yes | `avg_repeated_tool_calls` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | retry_count | `retry_count` yes | `avg_retry_count` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | turn_count | `turn_count` yes | `avg_turn_count` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | token_usage | `token_usage` yes | `avg_token_usage` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | command_failure_count | `command_failure_count` yes | `avg_command_failures` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | time_to_first_edit | `time_to_first_edit` yes | `avg_time_to_first_edit` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | time_to_first_test | `time_to_first_test` yes | `avg_time_to_first_test` yes | yes | yes | yes |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | failure_score | `failure_score` yes | `avg_failure_score` yes | yes | yes | yes |

## Nullable Metrics

`time_to_first_edit` and `time_to_first_test` are event-index metrics. Their aggregate averages use present values only; missing values mean the trace did not expose the corresponding edit or verification event.

| Manifest | Metric | Present | Missing | Mean semantics |
| --- | --- | ---: | ---: | --- |
| `benchmark/pilot/full30-real/runs.jsonl` | time_to_first_edit | 60 / 60 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/pilot/full30-real/runs.jsonl` | time_to_first_test | 60 / 60 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | time_to_first_edit | 20 / 20 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/hard/pilot/hard10-real/runs.jsonl` | time_to_first_test | 20 / 20 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | time_to_first_edit | 60 / 60 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/hard/pilot/hard30-real/runs.jsonl` | time_to_first_test | 60 / 60 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | time_to_first_edit | 24 / 24 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/process-stress/pilot/full-real/runs.jsonl` | time_to_first_test | 24 / 24 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | time_to_first_edit | 16 / 16 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/verification-lift/pilot/full-real/runs.jsonl` | time_to_first_test | 16 / 16 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | time_to_first_edit | 16 / 16 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/verification-lift-v2/pilot/full-real/runs.jsonl` | time_to_first_test | 16 / 16 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | time_to_first_edit | 8 / 8 | 0 | averages use present values only; missing values indicate no observed event |
| `benchmark/verification-ablation/pilot/full-real/runs.jsonl` | time_to_first_test | 4 / 8 | 4 | averages use present values only; missing values indicate no observed event |
