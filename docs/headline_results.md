# Headline Results Table

This generated table replaces the original expected-results sketch with the current stored evidence.

## Summary

- Ready: yes
- Ordinary verification-rate lift supported: no
- Waste reduction supported: yes
- No-verify ablation lift observed: yes
- Boundary: ordinary verification-rate lift is unsupported; no-verify ablation is a mechanism check only, not an ordinary baseline
- Source: `docs/results_summary.json`

## Table

| Metric | Baseline | Intervention | Delta | Interpretation |
| --- | ---: | ---: | ---: | --- |
| `hard10_success` | 0.70 | 0.80 | +0.10 | pilot-qualified success lift |
| `hard30_success` | 0.50 | 0.50 | +0.00 | flat hard30 success |
| `hard30_verification` | 1.00 | 1.00 | +0.00 | saturated; no ordinary verification lift |
| `hard30_repeated_tool_calls` | 12.93 | 9.20 | -3.73 | supported waste reduction |
| `hard30_unresolved_error_rate` | 0.00 | 0.00 | +0.00 | no unresolved-error movement |
| `hard30_token_usage` | 355.0k | 256.3k | -98.7k | supported waste reduction |
| `verification_lift_v2_verification` | 1.00 | 1.00 | +0.00 | ordinary-baseline retest is saturated |
| `verification_lift_v2_exact_verification` | 1.00 | 1.00 | +0.00 | exact visible success-check verification is saturated |
| `no_verify_ablation_verification` | 0.00 | 1.00 | +1.00 | mechanism check only; not an ordinary baseline |
| `no_verify_ablation_exact_verification` | 0.00 | 1.00 | +1.00 | mechanism check only; not an ordinary baseline |

Interpretation: the hard30 and ordinary-baseline verification-lift-v2 pilots support waste reduction, not an ordinary verification-rate lift. The no-verify ablation demonstrates harness control over verification behavior under an artificial baseline condition, so it should not be reported as ordinary-baseline evidence.
