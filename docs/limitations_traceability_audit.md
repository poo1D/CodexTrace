# Limitations Traceability Audit

This generated audit checks that the paper draft's Threats To Validity section carries the safe paper-language claims from the generated validity-threat map.

## Summary

- Ready: yes
- Threats covered: 7 / 7
- Validity map: `docs/validity_threats.json`
- Paper draft: `docs/paper_draft.md`

## Threat Coverage

| Threat | ID | Paper language present | Paper language | Covered |
| --- | --- | --- | --- | --- |
| `internal_validity` | yes | yes | Trace-only rules diagnose process failures but do not prove semantic correctness. | yes |
| `construct_validity` | yes | yes | Verification-rate lift is a negative boundary result, not a supported headline claim. | yes |
| `external_validity` | yes | yes | Results are pilot-scale and Codex-CLI-specific. | yes |
| `conclusion_validity` | yes | yes | Waste reduction is the strongest current RQ3 result; success lift remains pilot-qualified. | yes |
| `detector_validity` | yes | yes | Detector results are boundary results for observable process failures; hidden semantic recall is 0.00 with FN=30. | yes |
| `ablation_validity` | yes | yes | No-verify ablation is not ordinary-baseline evidence. | yes |
| `reproducibility_validity` | yes | yes | The artifact is reproducible for offline analysis, while new live collections may vary. | yes |

Interpretation: this audit links reviewer-facing validity caveats back into the paper draft. It does not judge whether the prose is sufficient for a particular venue.
