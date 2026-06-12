# Detector Label Evaluation

## Summary

| Metric | Value |
| --- | ---: |
| labels | 3 |
| micro_precision | 1 |
| micro_recall | 0.7778 |
| micro_f1 | 0.875 |
| macro_f1 | 0.6667 |

## Per-Label Scores

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hidden_semantic_edge_case | 0 | 0 | 2 | 0 | 0 | 0 |
| premature_completion | 3 | 0 | 0 | 1 | 1 | 1 |
| verification_gap | 4 | 0 | 0 | 1 | 1 | 1 |

## Runs

| Task | Prompt | Expected | Predicted | FP | FN |
| --- | --- | --- | --- | --- | --- |
| VAB-001 | baseline | premature_completion, verification_gap | premature_completion, verification_gap | - | - |
| VAB-001 | intervention | - | - | - | - |
| VAB-002 | baseline | hidden_semantic_edge_case, premature_completion, verification_gap | premature_completion, verification_gap | - | hidden_semantic_edge_case |
| VAB-002 | intervention | hidden_semantic_edge_case | - | - | hidden_semantic_edge_case |
| VAB-003 | baseline | verification_gap | verification_gap | - | - |
| VAB-003 | intervention | - | - | - | - |
| VAB-004 | baseline | premature_completion, verification_gap | premature_completion, verification_gap | - | - |
| VAB-004 | intervention | - | - | - | - |
