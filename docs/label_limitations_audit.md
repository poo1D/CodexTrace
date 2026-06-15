# Label Limitations Audit

This generated audit checks that manual-label provenance is paired with safe paper limitations.

## Summary

- Ready: yes
- Checks passed: 8 / 8
- Missing checks: 0
- Paper draft: `docs/paper_draft.md`
- Label provenance: `docs/label_provenance_audit.md`

## Checks

| Check | Status | Expected |
| --- | --- | --- |
| `hidden_grader_basis` | pass | hidden grader outcomes and qualitative inspection |
| `single_artifact_caveat` | pass | single-artifact diagnostic labels |
| `no_inter_annotator_claim` | pass | not inter-annotator-agreement evidence |
| `richer_labels_needed` | pass | richer process failure labels |
| `provenance_ready` | pass | Ready: yes |
| `provenance_failure_notes` | pass | Failure rows with notes: 30 / 30 |
| `provenance_inter_annotator_caveat` | pass | does not prove inter-annotator agreement |
| `no_gold_label_claim` | pass | no gold-label or inter-annotator-agreement claim |

Interpretation: this audit guards against treating single-artifact manual diagnostic labels as broad gold-standard process labels or inter-annotator-agreement evidence.
