# Paper Abstract Audit

This generated audit checks that the paper abstract states the current evidence-backed boundary-result thesis without overclaiming.

## Summary

- Ready: yes
- Checks passed: 15 / 15
- Missing checks: 0
- Abstract words: 287
- Paper draft: `docs/paper_draft.md`

## Checks

| Check | Status | Expected |
| --- | --- | --- |
| `codextrace_system` | pass | We introduce CodexTrace |
| `offline_parser` | pass | offline parser and diagnosis engine |
| `seven_pilots` | pass | seven real Codex benchmark pilots |
| `verification_negative` | pass | do not support a verification-rate-lift claim |
| `full30_waste` | pass | 10.43 to 7.00 |
| `full30_tokens` | pass | 218.7k to 184.8k |
| `hard30_success_flat` | pass | success rate stays flat at 50% |
| `hard30_repeated_calls` | pass | 12.93 to 9.20 |
| `hard30_tokens` | pass | 355.0k to 256.3k |
| `hard30_failure_score` | pass | 3.50 to 1.17 |
| `hidden_semantic_boundary` | pass | 30 hidden semantic edge-case failures |
| `semantic_oracles` | pass | strong semantic oracles |
| `process_failures` | pass | observable process failures |
| `no_unqualified_verification_lift` | pass | no unqualified verification-rate lift claim |
| `no_hidden_correctness_claim` | pass | no trace-only hidden-correctness claim |

Interpretation: the abstract is ready only if it includes the supported waste-reduction and trace-boundary results while avoiding the unsupported ordinary verification-rate-lift claim.
