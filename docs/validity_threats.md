# Validity Threats Audit

This generated audit maps paper validity threats to evidence, mitigations, and safe wording.

## Summary

- Ready: yes
- Threats covered: 7 / 7
- Boundary decision: revise_to_boundary_result_paper
- Ordinary verification-rate lift supported: no

## Threat Map

| Threat area | Threat | Evidence | Mitigation | Paper language |
| --- | --- | --- | --- | --- |
| `internal_validity` | Hidden graders may expose failures that visible trace process signals cannot explain. | hard30 visible traces often verify cleanly, but hidden graders expose 30 failures and 30 trace-only false negatives; process-stress adds 2 failures and 2 false negatives; verification-lift adds 2 failures and 2 false negatives. | Report trace diagnosis as process-level evidence and keep hidden-grader outcome oracles separate. | Trace-only rules diagnose process failures but do not prove semantic correctness. |
| `construct_validity` | Verification rate is saturated, so it is a weak construct for intervention benefit on current tasks. | hard30 verification delta is +0.00 and exact success-check delta is +0.00; process-stress verification delta is +0.00 and exact success-check delta is +0.00; verification-lift verification delta is +0.00 and exact success-check delta is +0.00; verification-lift-v2 verification delta is +0.00 and exact success-check delta is +0.00; stored ordinary/weak-baseline pilots are saturated. | Drop ordinary verification-rate lift as a finding and report waste metrics plus the no-verify ablation separately. | Verification-rate lift is a negative boundary result, not a supported headline claim. |
| `external_validity` | The artifact studies Codex CLI on pilot-scale fixture repositories, not all coding agents or SWE-bench-scale tasks. | full30 has 30 seed tasks; hard30 has 30 selected hard tasks and 60 real runs; readiness=True. | Frame results as a 30-task hard-tier pilot plus auxiliary stress tiers; avoid broad population claims. | Results are pilot-scale and Codex-CLI-specific. |
| `conclusion_validity` | Single paired runs per task can show directional deltas but not stable population estimates. | hard30 success 0.50->0.50; hard30 repeated calls 12.93->9.20; hard30 token usage 355.0k->256.3k. | Use paired-task deltas as pilot evidence and call for repeated trials before population claims. | Waste reduction is the strongest current RQ3 result; success lift remains pilot-qualified. |
| `detector_validity` | Rule-based detectors are interpretable but incomplete and can miss hidden semantic edge cases. | controlled detector fixtures cover 6 labels with micro-F1=1.00; hard30 includes 4 detected repetitive-exploration process positives (F1=1.00); full30 includes sandbox/permission TP=1, FP=0, FN=0, with 2 repetitive-exploration FP in the process-label slice. Hidden semantic recall is 0.00 with FN=30; process-stress hidden semantic FN=2; verification-lift hidden semantic FN=2. | Separate controlled-fixture detector coverage from natural real-pilot outcome detection. | Detector results are boundary results for observable process failures. |
| `ablation_validity` | The no-verify baseline is artificial and can overstate ordinary harness intervention effects. | verification-ablation verification delta is +1.00; exact success-check delta is +1.00; failure-score delta is -61.25. | Treat the no-verify tier only as a mechanism check. | No-verify ablation is not ordinary-baseline evidence. |
| `reproducibility_validity` | Real Codex collection depends on CLI behavior and environment state. | Stored traces, generated reports, manual labels, reproduction commands, and readiness gates are committed. | Support offline re-analysis without rerunning Codex; gate generated artifacts with tests and readiness checks. | The artifact is reproducible for offline analysis, while new live collections may vary. |

Interpretation: these threats are not blockers for a boundary-result paper, but they constrain the paper's wording and forbid broad verification-rate or hidden-correctness claims.
