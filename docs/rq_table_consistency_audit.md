# RQ Table Consistency Audit

This generated audit checks that the paper draft's RQ1-RQ4 result-table claims match the generated hard30 paper report.

## Summary

- Ready: yes
- RQs covered: 4 / 4
- Table checks covered: 10 / 10
- Paper draft: `docs/paper_draft.md`
- Hard30 report JSON: `benchmark/hard/pilot/hard30-real/paper-report-labeled.json`
- Hard30 report Markdown: `benchmark/hard/pilot/hard30-real/paper-report-labeled.md`

## Checks

| RQ | Check | Value | Paper | Report | Covered |
| --- | --- | --- | --- | --- | --- |
| RQ1 | `hidden_semantic_distribution` | yes | yes | yes | yes |
| RQ1 | `repetitive_distribution` | yes | yes | yes | yes |
| RQ2 | `hidden_semantic_detector_boundary` | yes | yes | yes | yes |
| RQ2 | `repetitive_detector_positive` | yes | yes | yes | yes |
| RQ3 | `hard30_flat_success` | yes | yes | yes | yes |
| RQ3 | `hard30_waste_reduction` | yes | yes | yes | yes |
| RQ3 | `paired_token_improvement` | yes | yes | yes | yes |
| RQ4 | `outcome_counts` | yes | yes | yes | yes |
| RQ4 | `verification_signal_boundary` | yes | yes | yes | yes |
| RQ4 | `unresolved_error_boundary` | yes | yes | yes | yes |

Interpretation: this audit guards the paper's RQ result tables against drift from generated hard30 report artifacts. It does not add new statistical evidence.
