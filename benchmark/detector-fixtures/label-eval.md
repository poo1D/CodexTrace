# Detector Label Evaluation

## Summary

| Metric | Value |
| --- | ---: |
| labels | 6 |
| micro_precision | 1 |
| micro_recall | 1 |
| micro_f1 | 1 |
| macro_f1 | 1 |

## Per-Label Scores

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| context_drift | 1 | 0 | 0 | 1 | 1 | 1 |
| premature_completion | 1 | 0 | 0 | 1 | 1 | 1 |
| repetitive_exploration | 1 | 0 | 0 | 1 | 1 | 1 |
| sandbox_permission_deadlock | 1 | 0 | 0 | 1 | 1 | 1 |
| unrecovered_tool_error | 2 | 0 | 0 | 1 | 1 | 1 |
| verification_gap | 2 | 0 | 0 | 1 | 1 | 1 |

## Runs

| Task | Prompt | Expected | Predicted | FP | FN |
| --- | --- | --- | --- | --- | --- |
| DF-001 | baseline | verification_gap | verification_gap | - | - |
| DF-002 | baseline | unrecovered_tool_error | unrecovered_tool_error | - | - |
| DF-003 | baseline | repetitive_exploration | repetitive_exploration | - | - |
| DF-004 | baseline | context_drift | context_drift | - | - |
| DF-005 | baseline | premature_completion, verification_gap | premature_completion, verification_gap | - | - |
| DF-006 | baseline | sandbox_permission_deadlock, unrecovered_tool_error | sandbox_permission_deadlock, unrecovered_tool_error | - | - |
