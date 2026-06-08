# Submission Readiness Plan

This plan tracks the gap between the current CodexTrace artifact and a stronger
paper submission for:

`When Coding Agents Get Lost: Trace-Based Diagnosis of Multi-Turn Tool-Use Failures`

The current repository is already useful as a GPU-free research artifact and CV
project. A stronger submission needs more evidence around scale, observable
process failures, and repeatability.

## Current Evidence Level

| Area | Current state | Submission risk |
| --- | --- | --- |
| System artifact | Parser, diagnosis engine, CLI, Web UI, benchmark runner, hidden-grader support. | Low. The system is implemented and CI-tested. |
| Seed benchmark | 30 tasks, 60 real Codex runs, all outcomes pass. | Medium. Good for waste analysis, weak for failure-distribution claims. |
| Hard benchmark | 50 runnable tasks; the paper-facing hard30 artifact has 30 selected tasks, 60 real Codex runs, and 30 outcome failures. | Medium. Stronger artifact, but single-trial success deltas remain pilot evidence. |
| Detector evaluation | Manual labels expose `TP=0`, `FP=0`, `FN=30` for hard30 hidden semantic edge cases. | Medium. Strong boundary result, but not enough positive process-failure labels. |
| RQ4 signal analysis | Hard30 signal table explains why clean traces can still fail hidden graders. | Medium. Needs more observable failures to identify predictive process signals. |

## Target For A Stronger Submission

The next stronger-submission target should be:

- Repeat hard30 trials or add randomized reruns for a subset of tasks.
- 60-100 additional hard-tier runs across baseline and intervention.
- At least 15-25 manually labeled outcome failures.
- A mix of hidden semantic failures and observable process failures.
- A paper draft whose main claims are supported by generated tables.

## Workstream 1: Repeat And Stress Hard30

Goal: move from one completed hard30 collection to a more stable estimate while
preserving hidden grader isolation. `HARD-011` through `HARD-050` are
implemented, and the selected hard30 pilot has been collected in
`benchmark/hard/pilot/hard30-real`.

The hard30 pilot selection is fixed in
`benchmark/hard/pilot/hard30-selection`. It keeps the evaluated hard10 pilot as
a prefix and adds 20 tasks selected for category and process-pressure coverage.
Collection runs as one shard per task with `scripts/run_hard30_shards.py`;
`scripts/merge_hard30_shards.py` creates the single `runs.jsonl` consumed by
the reporting tools. `scripts/finalize_hard30_pilot.py` generates the aggregate
tables, per-run CSV, manual-label template, and paper-report artifacts,
including `paired-task-deltas.csv` and `paired-task-summary.csv` for RQ3
analysis.

Hard30 collection plan:

| Area | Target count | Desired failure pressure |
| --- | ---: | --- |
| hidden semantic edge cases | 10-15 | Visible tests pass but hidden grader catches edge behavior. |
| multi-step feature changes | 5-10 | Agent must preserve earlier requirements while adding later ones. |
| error-recovery tasks | 5-8 | Initial verification fails and requires a targeted repair. |
| dependency/sandbox-friction tasks | 3-5 | Agent must adapt command strategy without deadlocking. |
| refactor-with-invariants tasks | 5-8 | Agent can over-edit or miss behavioral invariants. |

Completed acceptance criteria:

- The selected hard30 `tasks.jsonl` dry-runs to 60 baseline/intervention
  records.
- The selected hard30 shards dry-run and merge to 60 baseline/intervention
  records with configurable `--max-parallel` concurrency and per-shard
  `shard-run.json` failure metadata.
- Initial fixtures fail their hidden graders before agent edits.
- Prompt materialization keeps hidden grader details out of agent prompts.
- The selected tasks preserve category and expected failure-pressure coverage.

Remaining acceptance criteria:

- Repeat at least a subset of hard30 tasks to measure run-to-run variance.
- Add process-failure-heavy tasks or labels so RQ1/RQ2 are not dominated by
  `hidden_semantic_edge_case`.
- Re-run submission readiness after each collection with
  `scripts/check_submission_readiness.py`.

## Workstream 2: Improve Manual Labeling

Goal: make RQ1 and RQ2 stronger by labeling both outcome failures and
observable process failures.

Add labels for:

- `verification_gap`
- `unrecovered_tool_error`
- `repetitive_exploration`
- `context_drift`
- `premature_completion`
- `sandbox_permission_deadlock`
- `hidden_semantic_edge_case`

Acceptance criteria:

- Each failed run has at least one manual label.
- Each label includes a one-line rationale or evidence pointer.
- The label file can be evaluated by `codex-trace research evaluate-labels`.
- Positive examples exist for at least four process-level labels.

## Workstream 3: Repeatability And Variance

Goal: reduce the risk that observed improvements are one-off prompt or sampling
effects.

Recommended design:

- Run all hard tasks once under baseline and intervention.
- Re-run a stratified subset of 10-15 tasks with a second seed or fresh Codex
  session.
- Report aggregate means plus per-task paired deltas.

Acceptance criteria:

- Repeated subset has a separate manifest.
- Results summary reports whether intervention gains persist under repeats.
- Paper distinguishes pilot-scale evidence from stable estimates.

## Workstream 4: Better RQ4 Analysis

Goal: identify trace signals that explain observable failures, not only show
the hidden-semantic boundary.

Candidate additions:

- Per-signal effect sizes between success and failure outcomes.
- Per-label signal means for process-failure labels. The generated paper report
  now includes this table when manual labels are supplied.
- A simple threshold table for high-confidence warning signals.
- Optional logistic-regression or decision-stump analysis, only if sample size
  becomes large enough.

Acceptance criteria:

- RQ4 table separates at least one observable failure class.
- Hidden semantic failures remain reported as a boundary case.
- The paper does not overclaim trace-only prediction for semantic correctness.

## Workstream 5: Paper Polish

Goal: make the paper read like an honest systems/evaluation artifact, not a
demo writeup.

Required edits:

- Add an artifact availability paragraph.
- Add a clearer dataset construction table.
- Add a limitations paragraph that distinguishes process diagnosis from
  semantic correctness.
- Add a short "why no GPU is needed" method note.
- Keep all numeric claims tied to generated artifacts.

Acceptance criteria:

- `docs/paper_draft.md` can be read independently of the README.
- `docs/artifact_guide.md` gives a fast review path.
- `docs/reproducibility_checklist.md` maps every headline claim to evidence.

## Decision Gate

Treat the project as submission-ready only when:

- Hard tier has at least 30 tasks and 60 hard-tier runs.
- Detector evaluation includes both positive and negative examples for
  observable process failures.
- RQ3 improvement is visible in either success rate, waste metrics, or both.
- RQ3 paired task deltas identify which tasks improved, regressed, or stayed
  unchanged under intervention, with a paired summary suitable for the paper
  body.
- RQ4 has at least one signal analysis result beyond the hidden-semantic
  boundary.
- CI passes and all generated result tables can be reproduced from stored
  manifests.

The current machine-readable gate is:

```bash
PYTHONPATH=. python3 scripts/check_submission_readiness.py
```

It returns a non-zero exit code until the hard30 traces, generated tables, and
manual labels are present. Its report includes the next commands to run.
Failed-run manual labels must use known taxonomy tags and include non-empty
notes so RQ1/RQ2 claims remain auditable.
Use `scripts/audit_manual_labels.py` after editing `manual-labels.jsonl` to
summarize missing rows, missing notes, unknown tags, and per-tag coverage.

Until then, the honest positioning is:

> A reproducible pilot artifact showing that trace diagnosis can measure
> process failures and harness-level waste reductions, with an explicit boundary
> result for hidden semantic failures.
