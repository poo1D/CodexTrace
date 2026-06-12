# Detector Label Evaluation

## Summary

| Metric | Value |
| --- | ---: |
| labels | 2 |
| micro_precision | 0.3333 |
| micro_recall | 1 |
| micro_f1 | 0.5 |
| macro_f1 | 0.5 |

## Per-Label Scores

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| repetitive_exploration | 0 | 2 | 0 | 0 | 0 | 0 |
| sandbox_permission_deadlock | 1 | 0 | 0 | 1 | 1 | 1 |

## Runs

| Task | Prompt | Expected | Predicted | FP | FN |
| --- | --- | --- | --- | --- | --- |
| CT-001 | baseline | - | - | - | - |
| CT-001 | intervention | - | - | - | - |
| CT-006 | baseline | - | - | - | - |
| CT-006 | intervention | - | - | - | - |
| CT-011 | baseline | - | - | - | - |
| CT-011 | intervention | - | - | - | - |
| CT-016 | baseline | - | - | - | - |
| CT-016 | intervention | - | - | - | - |
| CT-021 | baseline | sandbox_permission_deadlock | repetitive_exploration, sandbox_permission_deadlock | repetitive_exploration | - |
| CT-021 | intervention | - | - | - | - |
| CT-026 | baseline | - | - | - | - |
| CT-026 | intervention | - | - | - | - |
| CT-028 | baseline | - | - | - | - |
| CT-028 | intervention | - | - | - | - |
| CT-002 | baseline | - | - | - | - |
| CT-002 | intervention | - | - | - | - |
| CT-003 | baseline | - | - | - | - |
| CT-003 | intervention | - | - | - | - |
| CT-004 | baseline | - | - | - | - |
| CT-004 | intervention | - | - | - | - |
| CT-005 | baseline | - | - | - | - |
| CT-005 | intervention | - | - | - | - |
| CT-007 | baseline | - | - | - | - |
| CT-007 | intervention | - | - | - | - |
| CT-008 | baseline | - | - | - | - |
| CT-008 | intervention | - | - | - | - |
| CT-009 | baseline | - | - | - | - |
| CT-009 | intervention | - | - | - | - |
| CT-010 | baseline | - | - | - | - |
| CT-010 | intervention | - | - | - | - |
| CT-012 | baseline | - | - | - | - |
| CT-012 | intervention | - | - | - | - |
| CT-013 | baseline | - | - | - | - |
| CT-013 | intervention | - | - | - | - |
| CT-014 | baseline | - | - | - | - |
| CT-014 | intervention | - | - | - | - |
| CT-015 | baseline | - | - | - | - |
| CT-015 | intervention | - | - | - | - |
| CT-017 | baseline | - | - | - | - |
| CT-017 | intervention | - | - | - | - |
| CT-018 | baseline | - | - | - | - |
| CT-018 | intervention | - | - | - | - |
| CT-019 | baseline | - | - | - | - |
| CT-019 | intervention | - | - | - | - |
| CT-020 | baseline | - | - | - | - |
| CT-020 | intervention | - | - | - | - |
| CT-022 | baseline | - | - | - | - |
| CT-022 | intervention | - | - | - | - |
| CT-023 | baseline | - | - | - | - |
| CT-023 | intervention | - | - | - | - |
| CT-024 | baseline | - | - | - | - |
| CT-024 | intervention | - | - | - | - |
| CT-025 | baseline | - | - | - | - |
| CT-025 | intervention | - | - | - | - |
| CT-027 | baseline | - | - | - | - |
| CT-027 | intervention | - | - | - | - |
| CT-029 | baseline | - | - | - | - |
| CT-029 | intervention | - | - | - | - |
| CT-030 | baseline | - | repetitive_exploration | repetitive_exploration | - |
| CT-030 | intervention | - | - | - | - |
