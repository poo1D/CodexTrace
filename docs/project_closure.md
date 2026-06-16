# CodexTrace Project Closure

This note freezes the current research direction as a boundary-result paper rather than continuing same-style experiments for the original verification-rate-lift thesis.

## Decision

- Close further same-style experiment collection for the current artifact.
- Submit or polish as a boundary-result paper.
- Do not claim ordinary-baseline verification-rate lift.
- Keep the no-verify ablation as a mechanism check only.
- Lead RQ3 with paired waste reduction and qualify success lift as pilot evidence.

## Evidence State

| Area | Closure status | Evidence |
| --- | --- | --- |
| Taxonomy | keep | Six observable process labels are covered by taxonomy docs, detector fixtures, and evidence-tier audits. |
| Benchmark | keep | The paper-facing hard30 artifact has 30 tasks and 60 paired Codex runs. |
| CodexTrace | keep | Stored traces can be parsed, diagnosed, aggregated, rendered, and replayed offline without GPU training. |
| Verification-rate lift | close as negative result | Non-ablation baseline verification is saturated: 98 / 98 baseline runs already verify, with broad and exact verification at 1.00. |
| Waste reduction | keep as strongest RQ3 result | Hard30 repeated tool calls drop 12.93 -> 9.20 and token usage drops 355.0k -> 256.3k. |
| Success lift | qualify | Hard10 improves 0.70 -> 0.80, while hard30 remains 0.50 -> 0.50. |
| RQ4 signals | keep as boundary result | Observable process positives are explained by trace signals, but hard30 hidden semantic failures have recall 0.00 with FN=30. |

## Stopped Work

- Do not run more same-style ordinary-baseline verification-lift experiments.
- Do not try to recover the original expected table by adding homogeneous runs.
- Do not continue adding audit layers unless they are needed for writing, packaging, or reviewer-facing clarity.

## Remaining Work

- Polish `docs/paper_draft.md` into the final submission format.
- Decide venue and page budget.
- Convert generated Markdown tables into manuscript tables or appendix material.
- If a stronger positive verification-rate claim is still desired later, start a new benchmark design with a non-saturated ordinary baseline; do not treat it as a continuation of the closed experiment.

## Final Framing

The project is useful as a trace-diagnosis and harness-waste paper. It is not evidence for the original claim that simple harness intervention raises ordinary Codex verification rate on these small tasks.
