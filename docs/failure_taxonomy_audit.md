# Failure Taxonomy Coverage Audit

This generated audit checks that the six target process-failure labels are defined, mapped in the paper draft, and covered by controlled detector fixtures.

## Summary

- Ready: yes
- Labels covered: 6 / 6
- Detector-fixture micro-F1: 1
- Taxonomy document: `docs/failure_taxonomy.md`
- Paper draft: `docs/paper_draft.md`
- Fixture evaluation: `benchmark/detector-fixtures/label-eval.json`

## Label Coverage

| Label | Taxonomy doc | Paper mapping | Fixture | Precision | Recall | F1 | Covered |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| verification_gap | yes | yes | yes | 1 | 1 | 1 | yes |
| unrecovered_tool_error | yes | yes | yes | 1 | 1 | 1 | yes |
| repetitive_exploration | yes | yes | yes | 1 | 1 | 1 | yes |
| context_drift | yes | yes | yes | 1 | 1 | 1 | yes |
| premature_completion | yes | yes | yes | 1 | 1 | 1 | yes |
| sandbox_permission_deadlock | yes | yes | yes | 1 | 1 | 1 | yes |

Interpretation: this audit proves rule-level taxonomy coverage, not broad natural-frequency coverage in real pilots. Real-pilot coverage is still described separately in `docs/results_summary.md` and `docs/paper_claim_audit.md`.
