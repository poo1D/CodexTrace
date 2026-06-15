# Failure Taxonomy Coverage Audit

This generated audit checks that the six target process-failure labels are defined, mapped in the paper draft, and covered by controlled detector fixtures.

## Summary

- Ready: yes
- Labels covered: 6 / 6
- Detector-fixture micro-F1: 1
- Real-pilot-positive labels: 2 / 6
- Ablation-positive labels: 2 / 6
- Fixture-only labels: 2 / 6
- Taxonomy document: `docs/failure_taxonomy.md`
- Paper draft: `docs/paper_draft.md`
- Fixture evaluation: `benchmark/detector-fixtures/label-eval.json`

## Label Coverage

| Label | Taxonomy doc | Paper mapping | Fixture | Precision | Recall | F1 | Real-pilot TP | Ablation TP | Evidence tier | Covered |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| verification_gap | yes | yes | yes | 1 | 1 | 1 | 0 | 4 | `ablation-positive` | yes |
| unrecovered_tool_error | yes | yes | yes | 1 | 1 | 1 | 0 | 0 | `fixture-only` | yes |
| repetitive_exploration | yes | yes | yes | 1 | 1 | 1 | 4 | 0 | `real-pilot-positive` | yes |
| context_drift | yes | yes | yes | 1 | 1 | 1 | 0 | 0 | `fixture-only` | yes |
| premature_completion | yes | yes | yes | 1 | 1 | 1 | 0 | 3 | `ablation-positive` | yes |
| sandbox_permission_deadlock | yes | yes | yes | 1 | 1 | 1 | 1 | 0 | `real-pilot-positive` | yes |

Interpretation: this audit proves rule-level taxonomy coverage and records each label's evidence tier. It does not imply broad natural-frequency coverage in real pilots; fixture-only labels still require careful boundary framing.
