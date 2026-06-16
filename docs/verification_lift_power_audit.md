# Verification-Lift Power and Headroom Audit

This generated audit checks whether current non-ablation evidence has enough verification-rate headroom to support the original expected verification-lift claim.

## Summary

- Ready: yes
- Non-ablation tiers: 6
- Baseline runs: 98
- Baseline runs without broad verification: 0
- Baseline runs without exact success-check verification: 0
- Observed baseline verification: 1.00
- Observed intervention verification: 1.00
- Empirical verification-rate headroom: 0.00
- Rule-of-three nonverification upper bound: 0.031
- Expected headline verification delta: 0.32
- Expected 51% -> 83% table compatible: no
- Ordinary expansion can close current claim without non-saturated baseline evidence: no
- Interpretation: stored ordinary and weak-baseline runs have no observed verification-rate headroom; additional same-style saturated runs cannot prove a positive rate lift

## Tier Headroom

| Tier | Baseline runs | Baseline broad | Baseline exact | Broad headroom | Exact headroom | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| full30 | 30 | 1.00 | 1.00 | 0.00 | 0.00 | saturated |
| hard10 | 10 | 1.00 | 1.00 | 0.00 | 0.00 | saturated |
| hard30 | 30 | 1.00 | 1.00 | 0.00 | 0.00 | saturated |
| process-stress | 12 | 1.00 | 1.00 | 0.00 | 0.00 | saturated |
| verification-lift | 8 | 1.00 | 1.00 | 0.00 | 0.00 | saturated |
| verification-lift-v2 | 8 | 1.00 | 1.00 | 0.00 | 0.00 | saturated |

## Claim-Closure Conditions

| Condition | Status | Evidence | Requirement |
| --- | --- | --- | --- |
| `non_saturated_ordinary_baseline` | `missing` | 0/98 broad baseline runs lack verification. | At least one non-ablation baseline run must omit broad or exact success-check verification before a positive rate lift has empirical headroom. |
| `positive_paired_rate_delta` | `missing` | All stored non-ablation broad and exact verification deltas are 0.00. | Intervention must improve broad or exact visible-success-check verification over the matched ordinary baseline. |
| `expected_headline_table` | `contradicted` | Observed ordinary/weak-baseline verification is 1.00, not 0.51; empirical headroom is 0.00, not the expected 0.32 delta. | The expected 51% -> 83% style result would require a non-saturated baseline population. |

Interpretation: this is not a substitute for a new positive experiment. It is a stopping rule for the current ordinary-baseline verification-rate claim: with 98 / 98 stored non-ablation baseline runs already verifying, the original rate-lift thesis lacks empirical headroom unless a future ordinary-baseline design first produces non-saturated baseline behavior.
