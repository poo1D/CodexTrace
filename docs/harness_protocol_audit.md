# Harness Protocol Audit

This generated audit checks that intervention prompt templates preserve the harness constraints named in the experiment design.

## Summary

- Ready: yes
- Intervention prompts covered: 4 / 4
- Harness rules per prompt: 5
- Protocol rules covered: 5 / 5
- Run-level proxy checks passed: 6 / 6
- Experiment protocol: `docs/experiment_protocol.md`
- Hard30 report: `benchmark/hard/pilot/hard30-real/paper-report-labeled.json`

## Prompt Coverage

| Prompt | Covered rules | Ready |
| --- | ---: | --- |
| `benchmark/prompts/intervention.txt` | 5 / 5 | yes |
| `benchmark/verification-lift/prompts/intervention.txt` | 5 / 5 | yes |
| `benchmark/verification-lift-v2/prompts/intervention.txt` | 5 / 5 | yes |
| `benchmark/verification-ablation/prompts/intervention.txt` | 5 / 5 | yes |

## Rule Coverage

| Rule | Protocol covered |
| --- | --- |
| `inspect_first` | yes |
| `minimal_edit` | yes |
| `post_edit_verification` | yes |
| `failure_diagnosis_before_retry` | yes |
| `finish_with_evidence` | yes |

## Run-Level Proxy Checks

| Constraint proxy | Baseline | Intervention | Delta | Status |
| --- | ---: | ---: | ---: | --- |
| `post_edit_verification_proxy` | 1 | 1 | 0 | pass |
| `verification_rate_proxy` | 1 | 1 | 0 | pass |
| `minimal_edit_proxy` | 9.1 | 4.533 | -4.567 | pass |
| `repetitive_exploration_proxy` | 12.93 | 9.2 | -3.733 | pass |
| `token_waste_proxy` | 355.0k | 256.3k | -98.7k | pass |
| `failed_command_proxy` | 0.3 | 0.1 | -0.2 | pass |

Interpretation: this audit verifies prompt-template and protocol coverage of the harness constraints, then links those constraints to hard30 aggregate trace-metric proxies. It does not prove that every model run obeyed each instruction.
