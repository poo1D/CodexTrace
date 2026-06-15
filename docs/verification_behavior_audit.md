# Verification Behavior Audit

This generated audit separates verification-rate lift from verification behavior under saturated ordinary pilots.

## Summary

- Ready: yes
- Non-ablation tiers saturated: 6 / 6
- Non-ablation tiers with earlier verification: 6 / 6
- Non-ablation tiers with leaner verify phase: 6 / 6
- No-verify ablation mechanism positive: yes
- Interpretation: ordinary verification rates are saturated; intervention changes verification timing and process cost, not the rate or depth of verification

## Non-Ablation Verification Behavior

| Tier | Baseline broad | Intervention broad | Baseline exact | Intervention exact | Time to first test delta | Verify-event delta | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| full30 | 1.00 | 1.00 | 1.00 | 1.00 | -0.67 | -2.47 | saturated rate; earlier and leaner verification path |
| hard10 | 1.00 | 1.00 | 1.00 | 1.00 | -1.60 | -3.60 | saturated rate; earlier and leaner verification path |
| hard30 | 1.00 | 1.00 | 1.00 | 1.00 | -1.90 | -3.93 | saturated rate; earlier and leaner verification path |
| process-stress | 1.00 | 1.00 | 1.00 | 1.00 | -0.75 | -0.58 | saturated rate; earlier and leaner verification path |
| verification-lift | 1.00 | 1.00 | 1.00 | 1.00 | -0.75 | -0.50 | saturated rate; earlier and leaner verification path |
| verification-lift-v2 | 1.00 | 1.00 | 1.00 | 1.00 | -2.00 | -3.88 | saturated rate; earlier and leaner verification path |

## Mechanism Ablation

| Tier | Baseline broad | Intervention broad | Baseline exact | Intervention exact | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| verification-ablation | 0.00 | 1.00 | 0.00 | 1.00 | mechanism-only evidence that the harness can force verification under an artificial no-verify baseline |

## Claim Boundary Verdicts

| Claim | Verdict | Evidence | Safe wording |
| --- | --- | --- | --- |
| Harness intervention improves ordinary-baseline verification rate. | `unsupported` | 6/6 non-ablation tiers are already saturated at broad and exact verification. | Report verification-rate saturation, not ordinary verification-rate lift. |
| Harness intervention reaches verification earlier under saturated ordinary pilots. | `supported` | 6/6 non-ablation tiers have lower average time_to_first_test. | Describe earlier verification as a process-behavior effect under saturated rates. |
| Harness intervention makes ordinary-pilot verification deeper. | `contradicted` | 6/6 non-ablation tiers have fewer verify-phase events under intervention. | Use leaner verification path, not deeper verification. |
| No-verify ablation shows harness control over verification behavior. | `mechanism-check-only` | No-verify ablation broad/exact verification changes 0.00->1.00. | Use only as an artificial-baseline mechanism check. |

Interpretation: this audit preserves the negative verification-rate result while giving RQ3 a process-level verification-behavior measurement. In the stored ordinary pilots, intervention reaches verification earlier and with fewer verify-phase events; this is leaner verification, not deeper verification.
