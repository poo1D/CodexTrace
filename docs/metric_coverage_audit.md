# Metric Coverage Audit

This generated audit checks that the metrics named in the experiment design are collected at run level, summarized for baseline/intervention comparison, emitted to CSV, and visible in generated aggregate Markdown.

## Summary

- Ready: yes
- Manifest checked: `benchmark/hard/pilot/hard30-real/runs.jsonl`
- Metrics covered: 11 / 11

## Coverage

| Metric | Run key | Summary key | CSV | Markdown | Covered |
| --- | --- | --- | --- | --- | --- |
| success_rate | `success` yes | `success_rate` yes | yes | yes | yes |
| verification_rate | `verification_rate` yes | `verification_rate` yes | yes | yes | yes |
| unresolved_error_rate | `unresolved_error` yes | `unresolved_error_rate` yes | yes | yes | yes |
| repeated_tool_call_count | `repeated_tool_call_count` yes | `avg_repeated_tool_calls` yes | yes | yes | yes |
| retry_count | `retry_count` yes | `avg_retry_count` yes | yes | yes | yes |
| turn_count | `turn_count` yes | `avg_turn_count` yes | yes | yes | yes |
| token_usage | `token_usage` yes | `avg_token_usage` yes | yes | yes | yes |
| command_failure_count | `command_failure_count` yes | `avg_command_failures` yes | yes | yes | yes |
| time_to_first_edit | `time_to_first_edit` yes | `avg_time_to_first_edit` yes | yes | yes | yes |
| time_to_first_test | `time_to_first_test` yes | `avg_time_to_first_test` yes | yes | yes | yes |
| failure_score | `failure_score` yes | `avg_failure_score` yes | yes | yes | yes |
