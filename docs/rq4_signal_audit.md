# RQ4 Signal Audit

This generated audit summarizes which trace signals explain observable process labels and where trace signals fail to explain hidden semantic outcome failures.

## Summary

- Ready for boundary-style RQ4 claim: yes
- Detector-fixture labels with top signals: 6
- Hard30 hidden semantic verification delta: +0.00
- Hard30 hidden semantic exact success-check delta: +0.00
- Hard30 hidden semantic unresolved-error delta: +0.00
- Expected label-signal checks passed: 6 / 6

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

## Expected Label-Signal Checks

| Label | Expected signals | Non-zero expected signals | Status |
| --- | --- | ---: | --- |
| context_drift | phase_inspect_events, token_usage, failure_score | 3 / 3 | pass |
| premature_completion | failure_score, phase_edit_events, time_to_first_edit | 3 / 3 | pass |
| repetitive_exploration | repeated_tool_call_count, phase_inspect_events, failure_score | 3 / 3 | pass |
| sandbox_permission_deadlock | unresolved_error, command_failure_count, phase_recover_events | 3 / 3 | pass |
| unrecovered_tool_error | unresolved_error, command_failure_count, phase_recover_events | 3 / 3 | pass |
| verification_gap | failure_score, phase_edit_events, time_to_first_test | 3 / 3 | pass |

## Expected Signal Detail

| Label | Signal | Delta label-baseline | Non-zero |
| --- | --- | ---: | --- |
| context_drift | phase_inspect_events | 1.5 | yes |
| context_drift | token_usage | 14.6k | yes |
| context_drift | failure_score | -20.83 | yes |
| premature_completion | failure_score | 29.17 | yes |
| premature_completion | phase_edit_events | 0.5 | yes |
| premature_completion | time_to_first_edit | 2 | yes |
| repetitive_exploration | repeated_tool_call_count | 0.8333 | yes |
| repetitive_exploration | phase_inspect_events | 2.5 | yes |
| repetitive_exploration | failure_score | -20.83 | yes |
| sandbox_permission_deadlock | unresolved_error | 0.6667 | yes |
| sandbox_permission_deadlock | command_failure_count | 0.6667 | yes |
| sandbox_permission_deadlock | phase_recover_events | 1.5 | yes |
| unrecovered_tool_error | unresolved_error | 0.6667 | yes |
| unrecovered_tool_error | command_failure_count | 0.6667 | yes |
| unrecovered_tool_error | phase_recover_events | 1 | yes |
| verification_gap | failure_score | 11.67 | yes |
| verification_gap | phase_edit_events | 1 | yes |
| verification_gap | time_to_first_test | -0.3333 | yes |

## RQ4 Signal Verdicts

| Claim | Verdict | Evidence | Safe wording |
| --- | --- | --- | --- |
| Trace signals explain controlled observable process labels. | `supported` | 6/6 expected label-signal checks pass. | Use expected signal checks as rule-level process-signal evidence. |
| Trace signals explain observed real process positives. | `supported-with-boundary` | Hard30 repetitive_exploration top signals=5; full30 sandbox_permission_deadlock top signals=5. | Claim explanation for reviewed observable process positives, not all outcomes. |
| Trace signals predict hidden semantic outcome failures. | `unsupported` | Hard30 hidden semantic deltas for verification, exact success-check verification, and unresolved_error are +0.00, +0.00, +0.00. | State that hidden semantic failures can look procedurally clean. |
| Failure score or token usage alone ranks hidden correctness. | `unsupported` | Hard30 hidden semantic token delta=-1771.6; failure-score delta=+1.00. | Keep token/failure-score claims process-scoped and pair them with task oracles. |

Interpretation: RQ4 is best framed as a boundary result. Process signals explain observable process failures such as repeated exploration and sandbox friction, but hidden semantic failures can look procedurally clean.
