# Expected Results Reconciliation Audit

This generated audit checks that paper-facing files use the stored headline evidence instead of the original expected-results sketch.

## Summary

- Ready: yes
- Paper files clean: 5 / 5
- Headline phrases present: 7 / 7
- Expected sketch replacements: 5
- Headline table: `docs/headline_results.md`

## Paper-Facing Files

| File | Clean | Forbidden expected strings |
| --- | --- | --- |
| `README.md` | yes | - |
| `docs/paper_draft.md` | yes | - |
| `docs/headline_results.md` | yes | - |
| `docs/submission_package.md` | yes | - |
| `docs/reproducibility_checklist.md` | yes | - |

## Headline Evidence

| Required phrase | Present |
| --- | --- |
| `This generated table replaces the original expected-results sketch with the current stored evidence.` | yes |
| `Ordinary verification-rate lift supported: no` | yes |
| `Waste reduction supported: yes` | yes |
| `ordinary verification-rate lift is unsupported; no-verify ablation is a mechanism check only, not an ordinary baseline` | yes |
| `\| `hard30_success` \| 0.50 \| 0.50 \| +0.00 \| flat hard30 success \|` | yes |
| `\| `hard30_verification` \| 1.00 \| 1.00 \| +0.00 \| saturated; no ordinary verification lift \|` | yes |
| `\| `hard30_token_usage` \| 355.0k \| 256.3k \| -98.7k \| supported waste reduction \|` | yes |

## Expected Sketch Replacement Map

| Sketch metric | Original expected | Stored evidence | Paper status |
| --- | --- | --- | --- |
| `success_rate` | `42% -> 58%` | hard30 0.50 -> 0.50; hard10 0.70 -> 0.80 | flat hard30; pilot-qualified hard10 lift |
| `verification_rate` | `51% -> 83%` | hard30 1.00 -> 1.00; verification-lift-v2 1.00 -> 1.00 | ordinary-baseline verification-rate lift unsupported |
| `repeated_tool_calls` | `6.4 -> 3.1` | hard30 12.93 -> 9.20 | supported waste reduction |
| `unresolved_errors` | `2.2 -> 0.9` | hard30 0.00 -> 0.00 | no unresolved-error movement |
| `token_usage` | `18.7k -> 15.2k` | hard30 355.0k -> 256.3k | supported waste reduction |

Interpretation: this audit prevents the aspirational expected-results table from drifting back into the paper as evidence. It does not judge whether the current headline results are strong enough for a particular venue.
