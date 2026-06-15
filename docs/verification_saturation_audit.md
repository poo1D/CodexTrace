# Verification Saturation Audit

This generated audit checks whether stored non-ablation Codex pilots leave any rate headroom for an ordinary verification-rate-lift claim.

## Summary

- Ready: yes
- Non-ablation tiers saturated: 6 / 6
- Ordinary verification-rate lift supported: no
- Ordinary exact success-check verification lift supported: no
- No-verify ablation mechanism positive: yes
- Claim boundary: ordinary and weak-baseline pilots are saturated; no-verify ablation is mechanism-only

## Non-Ablation Tiers

| Tier | Runs | Baseline broad | Intervention broad | Broad delta | Baseline exact | Intervention exact | Exact delta | Saturated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| full30 | 60 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 0.00 | yes |
| hard10 | 20 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 0.00 | yes |
| hard30 | 60 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 0.00 | yes |
| process-stress | 24 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 0.00 | yes |
| verification-lift | 16 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 0.00 | yes |
| verification-lift-v2 | 16 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 0.00 | yes |

## Mechanism Ablation

| Tier | Runs | Baseline broad | Intervention broad | Broad delta | Baseline exact | Intervention exact | Exact delta | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| verification-ablation | 8 | 0.00 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | mechanism-only, not ordinary baseline |

Interpretation: the stored ordinary and weak-baseline pilots do not support a verification-rate-lift finding because broad and exact visible-success-check verification are already saturated. The no-verify ablation shows harness control over verification behavior but cannot close the ordinary-baseline claim.
