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
- Real-pilot-positive process labels: 2 / 6
- Ablation-positive process labels: 2 / 6
- Fixture-only process labels: 2 / 6
- Process rule mechanisms mapped: 6 / 6

## Controlled Fixture Coverage

| Label | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `verification_gap` | 2 | 0 | 0 | 1 | 1 | 1 |
| `unrecovered_tool_error` | 2 | 0 | 0 | 1 | 1 | 1 |
| `repetitive_exploration` | 1 | 0 | 0 | 1 | 1 | 1 |
| `context_drift` | 1 | 0 | 0 | 1 | 1 | 1 |
| `premature_completion` | 1 | 0 | 0 | 1 | 1 | 1 |
| `sandbox_permission_deadlock` | 1 | 0 | 0 | 1 | 1 | 1 |

## Evidence Tier By Process Label

| Label | Controlled fixture | Real-pilot TP | Ablation TP | Evidence tier |
| --- | --- | ---: | ---: | --- |
| `verification_gap` | yes | 0 | 4 | `ablation-positive` |
| `unrecovered_tool_error` | yes | 0 | 0 | `fixture-only` |
| `repetitive_exploration` | yes | 4 | 0 | `real-pilot-positive` |
| `context_drift` | yes | 0 | 0 | `fixture-only` |
| `premature_completion` | yes | 0 | 3 | `ablation-positive` |
| `sandbox_permission_deadlock` | yes | 1 | 0 | `real-pilot-positive` |

## Process Rule Mechanism Map

| Label | Finding code | Trace signal | Evidence tier | Boundary note |
| --- | --- | --- | --- | --- |
| `verification_gap` | `verification_gap` | post-edit file changes without later test/build/lint verification | `ablation-positive` | Direct process signal; strongest current evidence is no-verify ablation. |
| `unrecovered_tool_error` | `command_failure_unhandled` | failed commands without a later similar recovery command or verification | `fixture-only` | Implemented rule; current evidence is controlled-fixture only. |
| `repetitive_exploration` | `repeated_search_or_read` | repeated search/read commands and high repeated tool-call volume | `real-pilot-positive` | Observed in hard30 real-pilot positives. |
| `context_drift` | `long_context_no_progress` | high context growth with weak edit or verification progress | `fixture-only` | V1 proxy; not a semantic task-keyword drift detector. |
| `premature_completion` | `premature_completion` | completion language emitted before verification evidence | `ablation-positive` | Direct process signal; strongest current evidence is no-verify ablation. |
| `sandbox_permission_deadlock` | `sandbox_or_permission_block` | sandbox, permission, network, or access-denied tool errors | `real-pilot-positive` | Observed in full30 real-pilot process labels. |

## Claim Boundary Verdicts

| Claim | Verdict | Evidence | Safe wording |
| --- | --- | --- | --- |
| Rules cover the six process-failure labels on controlled traces. | `supported` | 6/6 controlled labels, micro-F1=1. | Use as rule-level taxonomy coverage, not natural-frequency evidence. |
| Rules detect observed process-positive slices in real or ablation pilots. | `supported-with-boundary` | 2 real-pilot-positive labels, 2 ablation-positive labels, 2 fixture-only labels. | Claim detection of reviewed observable process positives and report evidence tiers. |
| Rules detect most real-world outcome failures. | `unsupported` | Hidden semantic false negatives total 36, including 30 hard30 false negatives. | Do not claim majority real-world failure detection; keep the claim process-scoped. |
| Rules detect hidden semantic correctness failures. | `contradicted` | Hidden semantic false negatives total 36. | State that hidden semantic failures require stronger task oracles or semantic checks. |

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
