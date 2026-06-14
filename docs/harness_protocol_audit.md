# Harness Protocol Audit

This generated audit checks that intervention prompt templates preserve the harness constraints named in the experiment design.

## Summary

- Ready: yes
- Intervention prompts covered: 4 / 4
- Harness rules per prompt: 5
- Protocol rules covered: 5 / 5
- Experiment protocol: `docs/experiment_protocol.md`

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

Interpretation: this audit verifies prompt-template and protocol coverage of the harness constraints. It does not prove that every model run obeyed each instruction; run-level behavior is measured separately through trace metrics and labels.
