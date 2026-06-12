# Paper Number Guard

This generated guard checks that paper-draft numeric claims match stored aggregate artifacts.

OK: yes
Checked snippets: 9
Missing snippets: 0

| Claim | Status | Expected snippet |
| --- | --- | --- |
| abstract full30 waste | present | `the intervention reduces repeated tool calls from 10.43 to 7.00 and average token usage from 218.7k to 184.8k` |
| abstract hard30 waste | present | `success rate stays flat at 50%, but the intervention reduces repeated tool calls from 12.93 to 9.20, average token usage from 355.0k to 256.3k` |
| full30 failure-score row | present | `| avg_failure_score | 4.17 | 1.00 | -3.17 |` |
| hard10 token row | present | `| avg_token_usage | 248.9k | 187.5k | -61.4k |` |
| hard30 waste row | present | `| avg_token_usage | 355.0k | 256.3k | -98.7k |` |
| hard30 paired task counts | present | `token usage improves in 26 of 30 tasks, repeated tool calls improve in 26 of 30 tasks` |
| process-stress paragraph | present | `flat at 0.92 -> 0.92, while repeated tool calls improve from 8.08 to 7.17 and token usage improves from 209.0k to 185.1k` |
| verification-lift paragraph | present | `verification both remain 1.00 -> 1.00, success remains 0.88 -> 0.88, repeated` |
| verification-ablation paragraph | present | `verification both rise from 0.00 to 1.00 and failure score drops from 61.25 to 0.00` |
