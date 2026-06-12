# RQ4 Signal Audit

This generated audit summarizes which trace signals explain observable process labels and where trace signals fail to explain hidden semantic outcome failures.

## Summary

- Ready for boundary-style RQ4 claim: yes
- Detector-fixture labels with top signals: 6
- Hard30 hidden semantic verification delta: +0.00
- Hard30 hidden semantic exact success-check delta: +0.00
- Hard30 hidden semantic unresolved-error delta: +0.00

## Hidden Semantic Boundary

| Signal | Delta success-failure | Interpretation |
| --- | ---: | --- |
| verification_rate | +0.00 | Hidden failures are still verified. |
| success_check_verification_rate | +0.00 | Hidden failures still run the visible success check. |
| unresolved_error | +0.00 | Hidden failures do not leave unresolved tool errors. |
| token_usage | -1771.6 | Token usage does not reliably expose hidden correctness. |
| failure_score | +1.00 | Process failure score does not rank hidden correctness. |

## Real Process Positives

### Hard30 Repetitive Exploration

| Signal | Label mean | Baseline mean | Delta label-baseline |
| --- | ---: | ---: | ---: |
| token_usage | 666.8k | 306.5k | 360.2k |
| failure_score | 28.75 | 1.833 | 26.92 |
| repeated_tool_call_count | 24.25 | 10.8 | 13.45 |
| phase_verify_events | 21.5 | 8.167 | 13.33 |
| phase_edit_events | 14 | 7.133 | 6.867 |

### Full30 Sandbox/Permission

| Signal | Label mean | Baseline mean | Delta label-baseline |
| --- | ---: | ---: | ---: |
| token_usage | 529.2k | 201.8k | 327.5k |
| failure_score | 55 | 2.583 | 52.42 |
| phase_recover_events | 32 | 1.233 | 30.77 |
| repeated_tool_call_count | 25 | 8.717 | 16.28 |
| command_failure_count | 5 | 0.35 | 4.65 |

## Controlled Detector Fixtures

| Label | Top signal | Delta label-baseline |
| --- | --- | ---: |
| context_drift | token_usage | 14.6k |
| premature_completion | token_usage | -3.3k |
| repetitive_exploration | token_usage | -521.7 |
| sandbox_permission_deadlock | token_usage | -4.3k |
| unrecovered_tool_error | token_usage | -4.2k |
| verification_gap | token_usage | -2.9k |

Interpretation: RQ4 is best framed as a boundary result. Process signals explain observable process failures such as repeated exploration and sandbox friction, but hidden semantic failures can look procedurally clean.
