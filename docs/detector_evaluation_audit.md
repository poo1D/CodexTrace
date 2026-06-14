# Detector Evaluation Audit

This generated audit consolidates the detector precision/recall evidence used for RQ2.

## Summary

- Ready: yes
- Controlled process labels covered: 6 / 6
- Controlled detector micro-F1: 1
- Hard30 repetitive_exploration TP: 4
- Full30 sandbox_permission_deadlock TP: 1
- Verification-ablation verification_gap TP: 4
- Verification-ablation premature_completion TP: 3
- Hidden semantic false negatives: 36

## Controlled Fixture Coverage

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `verification_gap` | 2 | 0 | 0 | 1 | 1 | 1 |
| `unrecovered_tool_error` | 2 | 0 | 0 | 1 | 1 | 1 |
| `repetitive_exploration` | 1 | 0 | 0 | 1 | 1 | 1 |
| `context_drift` | 1 | 0 | 0 | 1 | 1 | 1 |
| `premature_completion` | 1 | 0 | 0 | 1 | 1 | 1 |
| `sandbox_permission_deadlock` | 1 | 0 | 0 | 1 | 1 | 1 |

## Observable Process Positives

| Slice | Label | TP | FP | FN | Precision | Recall | F1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `hard30` | `repetitive_exploration` | 4 | 0 | 0 | 1 | 1 | 1 |
| `full30_process` | `sandbox_permission_deadlock` | 1 | 0 | 0 | 1 | 1 | 1 |
| `verification_ablation` | `verification_gap` | 4 | 0 | 0 | 1 | 1 | 1 |
| `verification_ablation` | `premature_completion` | 3 | 0 | 0 | 1 | 1 | 1 |

## Hidden Semantic Boundary

| Slice | Label | TP | FP | FN | Precision | Recall | F1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `hard30` | `hidden_semantic_edge_case` | 0 | 0 | 30 | 0 | 0 | 0 |
| `process_stress` | `hidden_semantic_edge_case` | 0 | 0 | 2 | 0 | 0 | 0 |
| `verification_lift` | `hidden_semantic_edge_case` | 0 | 0 | 2 | 0 | 0 | 0 |
| `verification_ablation` | `hidden_semantic_edge_case` | 0 | 0 | 2 | 0 | 0 | 0 |

## False Positive Boundary

| Slice | Label | TP | FP | FN | Precision | Recall | F1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `full30_process` | `repetitive_exploration` | 0 | 2 | 0 | 0 | 0 | 0 |

Interpretation: deterministic process rules cover the six-label taxonomy on controlled fixtures and detect several observed process-positive slices, but they do not detect hidden semantic correctness failures.
