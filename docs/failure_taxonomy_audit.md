# Failure Taxonomy Coverage Audit

This generated audit checks that the six target process-failure labels are defined, mapped in the paper draft, and covered by controlled detector fixtures.

## Summary

- Ready: yes
- Labels covered: 6 / 6
- Detector-fixture micro-F1: 1
- Real-pilot-positive labels: 2 / 6
- Ablation-positive labels: 2 / 6
- Fixture-only labels: 2 / 6
- Hard30 hidden semantic false negatives: 30
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

## RQ1 Distribution Boundary

| Claim | Verdict | Evidence | Safe wording |
| --- | --- | --- | --- |
| CodexTrace defines the six target observable process-failure modes. | `supported` | 6/6 labels covered in taxonomy docs, paper mapping, and controlled fixtures. | Use as the RQ1 process-failure taxonomy. |
| Current real pilots naturally expose all six process-failure modes. | `unsupported` | 2/6 labels have real-pilot positives: `repetitive_exploration`, `sandbox_permission_deadlock`. | Report evidence tiers rather than claiming natural-frequency coverage for every label. |
| Some target process modes are only visible in ablation or controlled traces so far. | `boundary` | Ablation-positive labels: `verification_gap`, `premature_completion`; fixture-only labels: `unrecovered_tool_error`, `context_drift`. | Frame ablation and fixture evidence as rule coverage, not broad pilot prevalence. |
| Hard30 outcome failures reveal an additional hidden-semantic boundary. | `supported-boundary` | Hard30 hidden_semantic_edge_case false negatives: 30. | Describe hidden semantic failures separately from observable process-failure taxonomy. |

Interpretation: this audit proves rule-level taxonomy coverage and records each label's evidence tier. It does not imply broad natural-frequency coverage in real pilots; fixture-only labels still require careful boundary framing.
