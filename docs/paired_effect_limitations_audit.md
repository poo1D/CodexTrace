# Paired Effect Limitations Audit

This generated audit checks that task-paired RQ3 effect-size evidence is paired with pilot-scale and population-claim limitations.

## Summary

- Ready: yes
- Checks passed: 13 / 13
- Missing checks: 0
- Paper draft: `docs/paper_draft.md`
- Paired effects audit: `docs/paired_effects_audit.md`

## Checks

| Check | Status | Expected |
| --- | --- | --- |
| `paired_audit_ready` | pass | Ready: yes |
| `hard30_paired_tasks` | pass | Hard30 paired tasks: 30 |
| `hard30_repeated_delta` | pass | Hard30 repeated tool-call delta: -3.733 |
| `hard30_token_delta` | pass | Hard30 token-usage delta: -98.7k |
| `bootstrap_interval_table` | pass | 95% bootstrap CI |
| `sign_test_table` | pass | Sign p |
| `paired_audit_population_caveat` | pass | not population-level significance claims |
| `paper_pilot_evidence` | pass | pilot evidence |
| `paper_stable_population_caveat` | pass | stable population estimate |
| `paper_repeated_trials_needed` | pass | repeated trials |
| `paper_paired_audit_reference` | pass | docs/paired_effects_audit.md |
| `no_statistically_significant_population_effect` | pass | no statistically significant population effect overclaim |
| `no_proves_general_effect` | pass | no proves-general-effect overclaim |

Interpretation: the paired-effect evidence supports a current-sample RQ3 waste-reduction claim, while the paper must keep repeated trials and population-level significance claims out of the headline.
