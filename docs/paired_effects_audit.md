# Paired Effects Audit

This generated audit computes task-paired baseline-to-intervention effects for the stored CodexTrace pilots. Deltas are intervention minus baseline; positive is better for success and verification, while negative is better for waste/error metrics.

## Summary

- Ready: yes
- Studies covered: 7 / 7
- Metrics per study: 10
- Bootstrap samples: 2000
- Bootstrap seed: 20260614
- Non-ablation studies with lower repeated calls: 6 / 6
- Non-ablation studies with lower token usage: 6 / 6
- Hard30 paired tasks: 30
- Hard30 repeated tool-call delta: -3.733 [-5.033, -2.5]
- Hard30 token-usage delta: -98.7k [-154.6k, -54.6k]
- Hard30 verification delta: 0

## Hard30 Paired Metrics

| Metric | N | Improved | Regressed | Unchanged | Avg delta | 95% bootstrap CI | Sign p |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| success_delta | 30 | 1 | 1 | 28 | 0 | [-0.1, 0.1] | 1 |
| verification_delta | 30 | 0 | 0 | 30 | 0 | [0, 0] | - |
| success_check_verification_delta | 30 | 0 | 0 | 30 | 0 | [0, 0] | - |
| unresolved_error_delta | 30 | 0 | 0 | 30 | 0 | [0, 0] | - |
| repeated_tool_call_delta | 30 | 26 | 2 | 2 | -3.733 | [-5.033, -2.5] | 3e-06 |
| retry_delta | 30 | 3 | 0 | 27 | -0.2 | [-0.4333, 0] | 0.25 |
| command_failure_delta | 30 | 4 | 1 | 25 | -0.2 | [-0.5, 0] | 0.375 |
| turn_delta | 30 | 0 | 0 | 30 | 0 | [0, 0] | - |
| token_usage_delta | 30 | 26 | 4 | 0 | -98.7k | [-154.6k, -54.6k] | 5.9e-05 |
| failure_score_delta | 30 | 4 | 1 | 25 | -2.333 | [-5.667, 0] | 0.375 |

## Study-Level Waste Deltas

| Study | Role | Paired tasks | Success delta | Verification delta | Repeated call delta | Token delta | Repeated improved | Token improved |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full30 | non_ablation_pilot | 30 | 0 | 0 | -3.433 | -34.0k | 24 | 19 |
| hard10 | non_ablation_pilot | 10 | 0.1 | 0 | -3 | -61.4k | 9 | 9 |
| hard30 | non_ablation_pilot | 30 | 0 | 0 | -3.733 | -98.7k | 26 | 26 |
| process_stress | non_ablation_pilot | 12 | 0 | 0 | -0.9167 | -23.9k | 4 | 5 |
| verification_lift | non_ablation_pilot | 8 | 0 | 0 | -0.75 | -4.7k | 5 | 5 |
| verification_lift_v2 | non_ablation_pilot | 8 | 0 | 0 | -3.125 | -39.2k | 7 | 8 |
| verification_ablation | auxiliary_ablation | 4 | 0 | 1 | 1.25 | 26.3k | 0 | 1 |

Interpretation: this audit supports the RQ3 waste-reduction claim with paired task evidence. Bootstrap intervals describe the current task sample only; they are not population-level significance claims.
