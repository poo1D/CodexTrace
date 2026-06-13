# Verification-Lift Next Experiment Audit

This generated audit records whether current evidence closes the original ordinary-baseline verification-lift claim.

## Verdict

- OK: yes
- Original verification-lift claim closed: no
- Additional ordinary-baseline experiment required: no
- Claim revision required: yes
- No-verify ablation cannot close the ordinary-baseline claim.

## Current Evidence

| Tier | Tasks | Baseline verification | Intervention verification | Broad delta | Exact success-check delta | Interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| verification-lift | 8 | 1.00 | 1.00 | 0.00 | 0.00 | weak-baseline pilot is saturated |
| verification-lift-v2 | 8 | 1.00 | 1.00 | 0.00 | 0.00 | ordinary-baseline pilot is saturated |
| verification-ablation | 4 | 0.00 | 1.00 | 1.00 | 1.00 | mechanism ablation only |

## Prompt Constraints

- Current lift baseline allows skip: yes
- Ablation baseline forbids verification: yes
- Ordinary baseline required: yes
- No-verify ablation disallowed for original claim: yes

## Planned Ordinary-Baseline V2 Scaffold

- Exists: yes
- Ready: yes
- Pilot collected: yes
- Tasks: 8
- Materialized fixtures: 8
- Baseline prompt is ordinary: yes
- Intervention is evidence-gated: yes
- Audit: `docs/verification_lift_v2_plan_audit.json`

## Acceptance Gates

- `ordinary_baseline`: Baseline prompt must be ordinary or weak-baseline, not an explicit no-verify ablation. Rationale: A no-verify baseline can prove harness control but cannot close the original ordinary-baseline claim.
- `non_saturated_baseline_or_depth_metric`: Measure broad verification, exact visible success-check verification, and verification depth so saturation is visible. Rationale: The current weak-baseline pilot has baseline verification 1.00 and exact verification 1.00, leaving no rate headroom.
- `paired_task_count`: Collect at least 8 paired tasks and 16 real runs before treating the result as a verification-lift experiment. Rationale: This matches the current verification-lift tier size while avoiding single-task anecdotes.
- `claim_closure`: Close the original claim only if intervention verification rate or exact success-check verification increases over a non-ablation baseline. Rationale: If the non-ablation baseline remains saturated, keep the paper framed as a boundary result.
